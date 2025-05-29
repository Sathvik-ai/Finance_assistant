from fastapi import FastAPI, UploadFile
import whisper
import pyttsx3
import tempfile
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
model = whisper.load_model("base")
engine = pyttsx3.init()

# Allow access from Streamlit and orchestrator
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/stt")
async def speech_to_text(audio: UploadFile):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        temp_path = temp_audio.name
        temp_audio.write(await audio.read())

    result = model.transcribe(temp_path)
    os.remove(temp_path)
    return {"text": result["text"]}

@app.get("/tts")
def text_to_speech(text: str):
    engine.save_to_file(text, "output.mp3")
    engine.runAndWait()
    return {"message": "Audio saved as output.mp3"}
