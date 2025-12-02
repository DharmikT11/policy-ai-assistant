# 🛡️ Policy AI Assistant

An **Enterprise-Grade RAG (Retrieval Augmented Generation) Application** designed to analyze HR Policy documents. Users can upload PDF, DOCX, or TXT files, and the AI acts as an intelligent HR companion—answering questions, citing sources, and drafting professional emails based strictly on the uploaded policy rules.

---

## 🌟 Key Features

* **📄 Multi-Format Support:** Ingests PDF, Word (.docx), and Text files seamlessly.
* **🧠 Intelligent RAG Engine:** Uses **Google Gemini 2.0 Flash** for high-speed reasoning and **FAISS/MongoDB** for vector search.
* **⚖️ Fact-Checking:** The AI answers *only* from the document and cites specific sources/pages.
* **✍️ Agentic Capabilities:** Can draft emails (e.g., "Write a leave application") while adhering to policy rules (notice periods, etc.).
* **🎨 Premium UI:** Glassmorphism design, smooth animations, and a responsive layout built with React.
* **🛠️ Power Tools:** Copy to clipboard, export chat history, and quick-action suggestions.

---

## 🏗️ Tech Stack

### **Frontend**
* **React.js (Vite):** Blazing fast UI framework.
* **Modern CSS:** Custom Glassmorphism theme (No heavy libraries).
* **Lucide React:** Beautiful, lightweight icons.
* **React Markdown:** Renders AI responses with rich formatting.

### **Backend**
* **FastAPI (Python):** High-performance async API.
* **LlamaIndex / FAISS:** Vector storage and retrieval orchestration.
* **Google Gemini API:** LLM and Embedding models.
* **MongoDB Atlas:** Metadata and document storage.

---

## 🚀 Getting Started

Follow these instructions to run the project locally.

### **Prerequisites**
* Node.js (v18 or higher)
* Python (v3.10 or higher)
* MongoDB Atlas Account (Free tier)
* Google AI Studio Key (Gemini)

### **1. Clone the Repository**

git clone [https://github.com/DharmikT11/policy-ai-assistant.git](https://github.com/DharmikT11/policy-ai-assistant.git)
cd policy-ai-assistant

### **2. Backend Setup**

Navigate to the backend folder and set up the Python environment.
cd backend
python -m venv venv

    Windows:
    
    venv\Scripts\activate
    
    Mac/Linux:
    
    source venv/bin/activate
    
    Install Dependencies
    
    pip install -r requirements.txt
    
    Configure Environment Variables: Create a .env file in the backend/ folder:
    
    GOOGLE_API_KEY=your_gemini_api_key_here
    MONGODB_URI=your_mongodb_connection_string_here
    DB_NAME=policy_db
    COLLECTION_NAME=policy_chunks
    
    Start the Server:
    uvicorn app.main:app --reload
    Server will run at http://localhost:8000

### **3. Frontend Setup**

Open a new terminal and navigate to the frontend folder.
cd frontend
npm install
npm run dev

Client will run at http://localhost:5173

**📖 Usage Guide**

    * Upload: Drag and drop your HR Policy (PDF/DOCX) on the landing page.
    * Wait: The system chunks, embeds, and indexes the document (takes ~5-10 seconds).
    * Chat: You will be redirected to the workspace.
    * Ask: "What is the probation period?"
    * Task: "Draft an email for sick leave."
    * Tools: Use the sidebar to see file status or download the chat history.

**🤝 Contributing**

    * Contributions are welcome! Please fork the repository and create a pull request.
    * Fork the Project
    * Create your Feature Branch (git checkout -b feature/AmazingFeature)
    * Commit your Changes (git commit -m 'Add some AmazingFeature')
    * Push to the Branch (git push origin feature/AmazingFeature)
    * Open a Pull Request

**📄 License**

  Distributed under the MIT License. See LICENSE for more information.

  Built with ❤️ by Dharmik Thakkar
