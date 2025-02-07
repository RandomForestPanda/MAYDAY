# MAYDAY: A Pilot Assistance Tool  

Modern aviation has integrated AI into various systems, yet there remains a crucial gap where AI-driven assistance can enhance pilot decision-making. Leveraging **Generative AI and Large Language Models (LLMs)**, we developed **MAYDAY**, an AI-powered tool designed to assist pilots in real-time, reducing stress and improving situational awareness.  




## **Key Functionalities**  

### ✅ **1. Dynamic Checklist Generator**  
- Uses a **Retrieval-Augmented Generation (RAG)** approach.  
- Retrieves data from aircraft manuals, airline SOPs, and operational documents.  
- Generates **context-aware checklists** for both standard and emergency situations.  
- Supports **manual text input** and **speech-to-text functionality** for ease of use in real-world cockpit environments.  

### ⚠️ **2. Hazard Alert System**  
- Pilots can **describe minor system failures** via **speech input or manual text**.  
- MAYDAY predicts **potential cascading failures** and provides **early warnings** to help pilots take **proactive measures**.  

### ✈️ **3. 3D Glide Slope Visualizer**  
- Offers a **real-time 3D visualization** of the aircraft’s approach glide slope.  
- Detects deviations and **triggers go-around alerts** if the aircraft overshoots the ideal descent path.  

### 🌦 **4. Weather-Aware Flight Planning (🚧 In Progress)**  
- Integrates **real-time weather forecasts** into flight planning.  
- Assists in selecting **alternate airports** in case of adverse weather conditions.  

## **Technology Stack**  

- **LLM Generation**: Open-source **Hugging Face SLMs** with **remote inference via Mistral v0.3 7B**.  
- **Backend**: Python (FastAPI), FAISS for retrieval.  
- **Frontend**: Streamlit-based UI for pilot interaction.  
- **Speech-to-Text**: Integrated **voice input** for hands-free interaction.  
- **Deployment**: AWS EC2 instance for hosting.  

## **Installation & Usage**  

1. **Download & Unzip** the repository.  
2. **Install Dependencies:**  
   ```bash
     pip install -r requirements.txt
     python login.py
  
