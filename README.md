# 🤖 Agentic AI Assistant

A beginner-friendly **Agentic AI Assistant** built with Python, Google Gemini, and Streamlit. The project demonstrates how an AI agent can understand user requests, use tools/functions when required, and generate a final response.

## 🚀 Features

* 🤖 AI-powered conversational assistant
* 🧠 Gemini LLM integration
* 🔧 Tool / function calling
* 🔄 Agent-based workflow
* 💬 Interactive Streamlit interface
* ⚡ Python backend
* ❌ Basic API error handling
* 🧩 Separate frontend and backend architecture

## 🏗️ Project Architecture

```text
User
  ↓
Streamlit UI (app.py)
  ↓
Backend / Agent Logic (backend.py)
  ↓
Gemini LLM
  ↓
Tool / Function Calling
  ↓
Tool Result
  ↓
Final AI Response
  ↓
Streamlit UI
```

## 📁 Project Structure

```text
Agentic-AI-Assistant/
│
├── app.py              # Streamlit frontend
├── backend.py          # Agent/backend logic
├── requirements.txt    # Required Python packages
└── README.md           # Project documentation
```

## 🛠️ Technologies Used

* Python
* Google Gemini API
* Agentic AI
* Large Language Models (LLMs)
* Function / Tool Calling
* Streamlit
* Git & GitHub

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd Agentic-AI-Assistant
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your Gemini API Key

Create a `.env` file:

```text
GEMINI_API_KEY=your_api_key_here
```

**Never upload your API key or `.env` file to GitHub.**

### 4. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## 🧠 What I Learned

Through this project, I practiced:

* Understanding the difference between a normal LLM application and an AI agent
* Connecting an LLM API with a Python application
* Implementing tool/function calling
* Designing a simple agent workflow
* Separating frontend and backend logic
* Building an interactive AI application using Streamlit
* Managing Python dependencies
* Running and testing an AI application locally
* Using Git and GitHub for project version control

## 🎯 Future Improvements

* Add more tools to the agent
* Add conversation memory
* Add RAG capabilities
* Add multiple specialized agents
* Add agent evaluation
* Deploy the application online
* Improve UI/UX

## 👨‍💻 Author

**Haris Azeem**

AI Engineer | Deep Learning & Computer Vision | NLP & Generative AI

GitHub: `Haris5511`
