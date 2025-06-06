# 🧠📈 Multi-Agent Finance Assistant – Morning Market Briefs

A voice-enabled multi-agent system that delivers spoken market briefs to portfolio managers using a modular, open-source pipeline. Built with FastAPI microservices, Streamlit UI, Retrieval-Augmented Generation (RAG), and voice I/O, this system orchestrates a variety of specialized agents to extract, analyze, and communicate real-time financial insights.

---

## 🚀 Use Case: Morning Market Brief

At **8 AM** every trading day, a portfolio manager asks:

> “What’s our risk exposure in Asia tech stocks today, and highlight any earnings surprises?”

The system responds with:

> “Today, your Asia tech allocation is 22% of AUM, up from 18% yesterday.  
> TSMC beat estimates by 4%, Samsung missed by 2%.  
> Regional sentiment is neutral with a cautionary tilt due to rising yields.”

---

## 🧩 System Architecture

### 🔧 Agent Roles

| Agent         | Description |
|---------------|-------------|
| **API Agent** | Fetches real-time and historical data via Yahoo Finance, AlphaVantage APIs. |
| **Scraping Agent** | Extracts financial filings and earnings reports using lightweight Python loaders and optionally MCPs. |
| **Retriever Agent** | Indexes documents and stores embeddings via FAISS or Pinecone. Retrieves relevant content for queries. |
| **Analysis Agent** | Performs quantitative analysis on retrieved data (e.g., risk exposure computation). |
| **Language Agent** | Synthesizes natural language responses using LLMs (LangChain/CrewAI/LangGraph). |
| **Voice Agent** | Handles speech-to-text (Whisper) → LLM → text-to-speech (TTS) pipeline. |

---

## 🛠️ Tech Stack

| Layer           | Tools / Frameworks |
|-----------------|--------------------|
| Voice I/O       | OpenAI Whisper, TTS (Coqui, pyttsx3, or ElevenLabs) |
| Backend Agents  | Python, FastAPI, LangChain, CrewAI, LangGraph |
| Data Pipeline   | AlphaVantage, Yahoo Finance, BeautifulSoup, requests |
| Embeddings      | FAISS or Pinecone |
| Orchestration   | FastAPI microservices, Docker |
| Frontend        | Streamlit |
| Deployment      | Streamlit Cloud / Docker container |
| Logging & Docs  | Markdown, AI prompt logs, GitHub |

---

## 📂 Repository Structure

```bash
.
├── agents/
│   ├── api_agent/
│   ├── scraping_agent/
│   ├── retriever_agent/
│   ├── analysis_agent/
│   └── language_agent/
├── voice/
│   ├── stt.py
│   ├── tts.py
├── orchestrator/
│   └── router.py
├── data_ingestion/
│   ├── alpha_vantage_loader.py
│   ├── yahoo_finance_loader.py
├── streamlit_app/
│   └── app.py
├── docs/
│   └── ai_tool_usage.md
├── Dockerfile
├── requirements.txt
└── README.md
