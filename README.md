# 🧠 JARVIS – Personal AI Assistant

JARVIS is a personal AI assistant built using a **Retrieval-Augmented Generation (RAG)** architecture.  
It combines a modern chatbot interface with a vector database to store and retrieve knowledge, and is designed to work with a **self-hosted Large Language Model (LLM)** such as LLaMA.

---

##  Key Features

-  Conversational chatbot interface
-  Knowledge storage with semantic search
-  Vector-based retrieval using Pinecone
-  Text embeddings via SentenceTransformers
-  FastAPI backend
-  React + Vite frontend
-  Architecture ready for self-hosted LLMs (LLaMA / Ollama)

---

## System Architecture

User (Browser)
↓
React Frontend (Chat UI)
↓
FastAPI Backend
↓
Embedding Model (SentenceTransformers)
↓
Vector Database (Pinecone)
↓
LLM Service (Mocked / Self-hosted LLaMA)



The assistant uses **Retrieval-Augmented Generation (RAG)**:
1. User query is embedded
2. Relevant knowledge is retrieved from Pinecone
3. Retrieved context is injected into the LLM prompt
4. The assistant responds contextually

---

##  Technology Stack

### Frontend
- React
- Vite
- Tailwind CSS

### Backend
- Python
- FastAPI
- SentenceTransformers
- Pinecone Vector Database

### AI / ML
- Embedding Model: `all-MiniLM-L6-v2` (384 dimensions)
- LLM: Self-hosted capable (mock mode enabled for development)

---

##  Setup Instructions

### Clone the Repository


git clone https://github.com/your-username/jarvis-ai-assistant.git
cd jarvis-ai-assistant

Backend Setup


cd backend
python -m venv venv
venv\Scripts\activate    # Windows
pip install -r requirements.txt
Create a .env file inside backend/:

PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=jarvis-knowledge
Start the backend:
uvicorn app.main:app --reload
Backend URL:
http://localhost:8000

 Frontend Setup

cd frontend
npm install
npm run dev
Frontend URL:
http://localhost:5173
