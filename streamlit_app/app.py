import streamlit as st
import requests
import uuid
import os
import spacy
import subprocess
import importlib.util
from streamlit_audio_recorder import audio_recorder

st.set_page_config(page_title="Finance Assistant", layout="centered")
st.title("🎙️ Voice-Driven Market Brief Assistant")

def install_spacy_model():
    model_name = "en_core_web_sm"
    if importlib.util.find_spec(model_name) is None:
        subprocess.run(["python", "-m", "spacy", "download", model_name])

install_spacy_model()
nlp = spacy.load("en_core_web_sm")

st.markdown("### 🎧 Upload `.wav` or `.mp3` **or record your question**")

# Option 1: Upload audio file
audio_file = st.file_uploader("Upload audio question", type=["wav", "mp3"])

# Option 2: Record audio in browser
audio_bytes = audio_recorder()

filename = None

if audio_file is not None:
    # Save uploaded audio temporarily
    filename = f"temp_{uuid.uuid4().hex}.{audio_file.name.split('.')[-1]}"
    with open(filename, "wb") as f:
        f.write(audio_file.read())

    st.audio(filename)

elif audio_bytes is not None:
    # Save recorded audio bytes to temporary WAV file
    filename = f"temp_{uuid.uuid4().hex}.wav"
    with open(filename, "wb") as f:
        f.write(audio_bytes)

    st.audio(filename)

if filename is not None:
    # Send audio file to backend API for processing
    with open(filename, "rb") as f:
        try:
            response = requests.post(
                "http://localhost:8005/brief",  # Change URL if deployed elsewhere
                files={"audio": (filename, f)}
            )
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Failed to connect to backend: {e}")
            response = None

    # Remove temp file after sending
    os.remove(filename)

    if response and response.status_code == 200:
        data = response.json()
        st.markdown(f"**🧠 You asked:** `{data['query']}`")
        st.markdown("**📊 Summary:**")
        st.success(data["summary"])

        # Play AI voice summary if available
        if os.path.exists("output.mp3"):
            st.markdown("🔊 AI Voice Summary:")
            st.audio("output.mp3", format="audio/mp3")
    elif response:
        st.error(f"❌ Error {response.status_code}: {response.text}")
