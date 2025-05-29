import streamlit as st
import requests
import uuid
import os
import spacy
import subprocess
import importlib.util
from streamlit_webrtc import webrtc_streamer
import av
import numpy as np
import tempfile
import soundfile as sf

st.set_page_config(page_title="Finance Assistant", layout="centered")
st.title("🎙️ Voice-Driven Market Brief Assistant")

# def install_spacy_model():
#     model_name = "en_core_web_sm"
#     if importlib.util.find_spec(model_name) is None:
#         subprocess.run(["python", "-m", "spacy", "download", model_name])

# install_spacy_model()
nlp = spacy.load("en_core_web_sm")

st.markdown("### 🎧 Upload `.wav` or `.mp3` **or record your question using your microphone**")

# Option 1: Upload audio file
audio_file = st.file_uploader("Upload audio question", type=["wav", "mp3"])

# Option 2: Record audio from mic using streamlit-webrtc

class AudioProcessor:
    def __init__(self):
        self.frames = []

    def recv(self, frame: av.AudioFrame):
        # Collect audio frames
        pcm = frame.to_ndarray(format="s16")
        self.frames.append(pcm)
        return frame

webrtc_ctx = webrtc_streamer(
    key="audio-recorder",
    mode="sendrecv",
    audio_receiver_size=1024,
    video_frame_callback=None,
    media_stream_constraints={"audio": True, "video": False},
    audio_processor_factory=AudioProcessor,
    async_processing=True,
)

filename = None

def save_audio(frames, sample_rate=48000):
    # Concatenate all frames and save to WAV file
    audio = np.concatenate(frames, axis=1).T
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    sf.write(temp_file.name, audio, sample_rate)
    return temp_file.name

if audio_file is not None:
    # Save uploaded audio temporarily
    filename = f"temp_{uuid.uuid4().hex}.{audio_file.name.split('.')[-1]}"
    with open(filename, "wb") as f:
        f.write(audio_file.read())
    st.audio(filename)

elif webrtc_ctx.state.playing:
    if webrtc_ctx.audio_receiver:
        frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
        if frames:
            # Convert frames to numpy arrays
            pcm_frames = [frame.to_ndarray(format="s16") for frame in frames]
            # Save to temp wav file
            filename = save_audio(pcm_frames)
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
    if os.path.exists(filename):
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
