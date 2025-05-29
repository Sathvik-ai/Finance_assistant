import streamlit as st
import requests
import uuid
import os
import spacy

# Optional: Audio playback
import tempfile

# Page config
st.set_page_config(page_title="Finance Assistant", layout="centered")
st.title("🎙️ Voice-Driven Market Brief Assistant")

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

st.markdown("### 🎧 Upload `.wav` or `.mp3` audio file with your question")

# Upload audio
audio_file = st.file_uploader("Upload your question (audio)", type=["wav", "mp3"])

filename = None


if audio_file is not None:
    filename = f"temp_{uuid.uuid4().hex}.{audio_file.name.split('.')[-1]}"
    with open(filename, "wb") as f:
        f.write(audio_file.read())
    st.audio(filename)

    with open(filename, "rb") as f:
        try:
            response = requests.post(
                "http://localhost:8005/brief",  # 🔁 Change this if hosted elsewhere
                files={"audio": (filename, f)},
            )
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Failed to connect to backend: {e}")
            response = None

    # Remove temp file
    if os.path.exists(filename):
        os.remove(filename)

    # Handle response
    if response and response.status_code == 200:
        data = response.json()
        st.markdown(f"**🧠 You asked:** `{data['query']}`")
        st.markdown("**📊 Summary:**")
        st.success(data["summary"])

        # If audio reply exists
        if os.path.exists("output.mp3"):
            st.markdown("🔊 AI Voice Summary:")
            st.audio("output.mp3", format="audio/mp3")
    elif response:
        st.error(f"❌ Error {response.status_code}: {response.text}")
