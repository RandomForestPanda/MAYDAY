from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
import faiss
import pickle
from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
import redis
import json
import traceback

# Initialize Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

try:
    redis_client.ping()
    print("Connected to Redis!")
except redis.ConnectionError as e:
    print(f"Failed to connect to Redis: {e}")

# Load FAISS index and checklist data
faiss_index = faiss.read_index("knowledge_base/checklist_knowledge_base.index")
with open("knowledge_base/checklist_mapping.pkl", "rb") as f:
    checklists = pickle.load(f)

# Initialize FastAPI app
app = FastAPI()

# Initialize embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize Ollama model
llm = ChatOllama(model="gemma2:2b", temperature=0)

# Define the prompt template
prompt = PromptTemplate(
    template="""You are a pilot assistant. The user is a pilot. Based on the situation provided, generate relevant procedures, checklists, and tasks to guide the pilot.
    Answer in a clear, helpful, and actionable format:
    Question: {question}
    Documents: {documents}
    Answer:""",
    input_variables=["question", "documents"],
)

rag_chain = prompt | llm | StrOutputParser()

# Define Retriever
class FAISSRetriever:
    def __init__(self, faiss_index, checklists):
        self.faiss_index = faiss_index
        self.checklists = checklists

    def invoke(self, query, n_results=3):
        query_embedding = embedding_model.encode([query])
        distances, indices = self.faiss_index.search(query_embedding, n_results)
        documents = [Document(page_content=self.checklists[idx]) for idx in indices[0] if idx < len(self.checklists)]
        return documents

retriever = FAISSRetriever(faiss_index, checklists)

# Define RAGApplication
class RAGApplication:
    def __init__(self, retriever, rag_chain):
        self.retriever = retriever
        self.rag_chain = rag_chain

    def run(self, query, user_id):
        try:
            # Check Redis cache
            cache_key = f"user:{user_id}:cache:{query}"
            cached_response = redis_client.get(cache_key)
            if cached_response:
                print("Returning cached response!")
                return json.loads(cached_response)

            # Retrieve documents
            documents = self.retriever.invoke(query)
            doc_texts = "\n".join([doc.page_content for doc in documents])

            # Generate answer
            answer = self.rag_chain.invoke({"question": query, "documents": doc_texts})

            # Cache response
            redis_client.setex(cache_key, 3600, json.dumps(answer))  # Cache for 1 hour

            # Update user history
            history_key = f"user:{user_id}:history"
            redis_client.lpush(history_key, query)
            redis_client.ltrim(history_key, 0, 9)  # Keep only the last 10 queries

            return answer
        except Exception as e:
            print(f"Error in RAG application: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail="Error processing query.")

# Allow CORS
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

rag_application = RAGApplication(retriever, rag_chain)
print("RAG application created")

# Define request model
class QueryRequest(BaseModel):
    user_id: str
    query: str

# Search endpoint (Accept JSON instead of Form data)
@app.post("/search")
async def receive_search(request: QueryRequest):
    try:
        answer = rag_application.run(request.query, request.user_id)
        return {"response": answer}
    except Exception as e:
        print(f"Error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")
