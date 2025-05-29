import streamlit as st
import requests
import uuid
import os
import sounddevice as sd
import scipy.io.wavfile as wav
import spacy
import subprocess
import importlib.util

st.set_page_config(page_title="Finance Assistant", layout="centered")
st.title("🎙️ Voice-Driven Market Brief Assistant")

def install_spacy_model():
    model_name = "en_core_web_sm"
    if importlib.util.find_spec(model_name) is None:
        subprocess.run(["python", "-m", "spacy", "download", model_name])
        
install_spacy_model()
nlp = spacy.load("en_core_web_sm")

st.markdown("### 🎧 Upload `.wav` or `.mp3` **or record your question**")

# ---------- RECORD AUDIO ----------
def record_audio(duration=5, filename="recorded.wav"):
    fs = 44100  # Sample rate
    st.info("Recording...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait until recording is finished
    wav.write(filename, fs, recording)
    st.success("Recording complete.")
    return filename

# ----- Option 1: Upload -----
audio_file = st.file_uploader("Upload audio question", type=["wav", "mp3"])

# ----- Option 2: Record -----
use_mic = st.button("🎙️ Record 5 seconds from Mic")

# Decide source
if audio_file or use_mic:
    # Save audio file from upload or recording
    if audio_file:
        filename = f"temp_{uuid.uuid4().hex}.{audio_file.name.split('.')[-1]}"
        with open(filename, "wb") as f:
            f.write(audio_file.read())
    else:
        filename = record_audio()

    # Show player
    st.audio(filename)

    # Send to backend
    with open(filename, "rb") as f:
        response = requests.post(
            "http://localhost:8005/brief",
            files={"audio": (filename, f)}
        )

    os.remove(filename)

    if response.status_code == 200:
        data = response.json()
        st.markdown(f"**🧠 You asked:** `{data['query']}`")
        st.markdown("**📊 Summary:**")
        st.success(data["summary"])

        if os.path.exists("output.mp3"):
            st.markdown("🔊 AI Voice Summary:")
            st.audio("output.mp3", format="audio/mp3")
    else:
        st.error(f"❌ Error {response.status_code}: {response.text}")
