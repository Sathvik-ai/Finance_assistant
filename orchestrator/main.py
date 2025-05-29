from fastapi import FastAPI, UploadFile
import requests
import spacy

app = FastAPI()

# Microservice URLs
VOICE_AGENT = "http://localhost:8003"
API_AGENT = "http://localhost:8001"
SCRAPER_AGENT = "http://localhost:8002"
RETRIEVER_AGENT = "http://localhost:8004"
LANGUAGE_AGENT = "http://localhost:8006"


nlp = spacy.load("en_core_web_sm")

def extract_company_name(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT"]:
            return ent.text
    return None


@app.post("/brief")
async def generate_brief(audio: UploadFile):
    # Step 1: Speech-to-Text
    stt_response = requests.post(
        f"{VOICE_AGENT}/stt",
        files={"audio": (audio.filename, await audio.read())}
    )
    stt_response.raise_for_status()
    query = stt_response.json()["text"]
    company_name = extract_company_name(query)

    # Step 2: Retrieve top-k relevant chunks
    retriever_response = requests.get(
        f"{RETRIEVER_AGENT}/retrieve",
        params={"query": query, "company": company_name}
    )
    retriever_response.raise_for_status()
    chunks = retriever_response.json().get("results", [])

    # Step 3: Generate summary using LLM
    llm_response = requests.post(
        f"{LANGUAGE_AGENT}/summarize",
        json={"question": query, "chunks": chunks}
    )
    llm_response.raise_for_status()
    summary = llm_response.json()["summary"]

    # Step 4: Text-to-Speech
    tts_response = requests.get(
        f"{VOICE_AGENT}/tts",
        params={"text": summary}
    )
    tts_response.raise_for_status()

    return {
        "query": query,
        "company": company_name,
        "summary": summary,
        "audio_file": "output.mp3"
    }