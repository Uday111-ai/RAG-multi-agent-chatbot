# 🧠 RAG Chatbot System
A modular **Retrieval-Augmented Generation (RAG)** chatbot built using **Streamlit, LangChain, and ChromaDB**.  
This project demonstrates how large language models can be enhanced with external knowledge using a structured multi-agent pipeline.

---

## 🚀 Project Overview
This system allows users to ask questions and receive **context-aware answers** by retrieving relevant information from a vector database before generating a response.

Instead of relying only on the LLM's internal knowledge, this project uses a **Retrieval-Augmented approach**, improving accuracy and relevance.

---

## 🏗️ Architecture & Workflow

```
User Query
↓
Intent Detection
↓
Document Retrieval (Vector Search)
↓
Context Processing / Summarization
↓
Answer Generation (LLM)
↓
Final Response
```

### 🔍 Detailed Flow

#### 📄 Document Processing Phase
1. User uploads a document  
2. Ingestion Agent processes and stores embeddings in ChromaDB  

#### ❓ Query & Response Phase
3. User asks a query based on the document  
4. Orchestrator manages the pipeline  
5. Intent Agent classifies the query  
6. Retrieval Agent fetches relevant context  
7. Summarization Agent refines the context  
8. Answer Agent generates the response  
9. Final answer is displayed to the user  

---

## 📂 Project Structure

```
project/
│
├── agents/             # Modular agents (retrieval, intent, summarization, answer)
├── app.py              # Streamlit frontend (entry point)
├── orchestrator.py     # Controls pipeline flow
├── requirements.txt    # Project dependencies
├── .gitignore          # Ignore unnecessary files
├── .env.example        # Sample environment file
└── README.md           # Project documentation
```

---

## ⚙️ Core Components

### 🔹 Agents (Modular Design)
- **Ingestion Agent** → Processes and stores documents  
- **Retrieval Agent** → Fetches relevant data from vector DB  
- **Intent Agent** → Classifies user queries  
- **Summarization Agent** → Refines retrieved context  
- **Answer Agent** → Generates final response  

---

## 🧪 Setup Instructions (Local)

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/rag-chatbot.git
cd rag-chatbot
```

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Add Environment Variables
```bash
GROQ_API_KEY = your_api_key_here
```

### 5. Run the Application
```bash
python -m streamlit run app.py
```

---

## 🧩 Key Features

✅ Multi-agent modular architecture  
✅ Retrieval-Augmented Generation (RAG) pipeline  
✅ Semantic search using vector embeddings  
✅ Context-aware responses  
✅ Clean and extensible design  

---

## 🏁 Final Outcome

- Built a fully functional RAG-based chatbot  
- Implemented a scalable multi-agent architecture  
- Improved answer quality using retrieval augmentation  
- Maintained a clean and professional codebase  

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python | Core language |
| Streamlit | Frontend UI |
| LangChain | LLM orchestration |
| ChromaDB | Vector database |
| Groq API | Language model (LPU Inference) |

---

## 👨‍💻 Author

**Uday Maddheshiya**  
Final Year B.Tech — Computer Science & Engineering (AI & ML)
