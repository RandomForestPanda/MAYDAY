from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import json
import traceback
from huggingface_hub import InferenceClient

# Load FAISS index and checklist data
faiss_index = faiss.read_index(r"C:\Users\iamsa\VSCODE\Python\Project\knowledge_base\checklist_knowledge_base.index")
with open(r"C:\Users\iamsa\VSCODE\Python\Project\knowledge_base\checklist_mapping.pkl", "rb") as f:
    checklists = pickle.load(f)

# Initialize FastAPI app
app = FastAPI()

# Initialize embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Define the Hugging Face API Key and Inference Client
HF_API_KEY = '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'  # Replace with your actual HF API key
client = InferenceClient(api_key=HF_API_KEY)

# Define the prompt template
def generate_prompt(query, documents):
    return f"""
    You are a pilot assistant. The user is a pilot. Based on the situation provided through , generate detailed relevant checklists to execute, and tasks to guide the pilot to handle the emergency situation .
    Answer in a detailed, clear, helpful, and actionable format:
    Question: {query}
    Documents: {documents}
    Answer:
    """

# Function to query the Hugging Face Inference API using Mistral
def generate_answer_with_mistral(query, documents):
    prompt = generate_prompt(query, documents)
    messages = [
        {"role": "user", "content": prompt}
    ]

    try:
        # Send the request to Hugging Face InferenceClient (Mistral 7B model)
        completion = client.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.2",
            messages=messages,
            max_tokens=500
        )

        # Extract the generated response from the API
        answer = completion.choices[0].message["content"]
        return answer
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error contacting Hugging Face API: {str(e)}")

# Define Retriever
class FAISSRetriever:
    def __init__(self, faiss_index, checklists):
        self.faiss_index = faiss_index
        self.checklists = checklists

    def invoke(self, query, n_results=3):
        query_embedding = embedding_model.encode([query])
        distances, indices = self.faiss_index.search(query_embedding, n_results)
        documents = [checklists[idx] for idx in indices[0] if idx < len(self.checklists)]
        return documents

retriever = FAISSRetriever(faiss_index, checklists)

# Define RAGApplication
class RAGApplication:
    def __init__(self, retriever):
        self.retriever = retriever

    def run(self, query, user_id):
        try:
            # Print input query
            print(f"Input Query: {query}")

            # Retrieve documents
            documents = self.retriever.invoke(query)
            doc_texts = "\n".join(documents)

            # Print retrieved documents
            print(f"Retrieved Documents: {doc_texts}")

            # Generate answer using Hugging Face Inference API (Mistral 7B)
            answer = generate_answer_with_mistral(query, doc_texts)

            # Print final response
            print(f"Final Response: {answer}")

            return answer
        except Exception as e:
            print(f"Error in RAG application: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail="Error processing query.")

# Allow CORS
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"],
                   allow_headers=["*"])

rag_application = RAGApplication(retriever)
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
        print(answer)
        return {"response": answer}
    except Exception as e:
        print(f"Error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")
