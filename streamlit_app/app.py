import streamlit as st
import requests
import uuid
import os
import spacy
import tempfile
import numpy as np
import av
import soundfile as sf
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase

# Page config
st.set_page_config(page_title="Finance Assistant", layout="centered")
st.title("🎙️ Voice-Driven Market Brief Assistant")

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

st.markdown("### 🎧 Upload `.wav` or `.mp3` **or record your question using your microphone**")

# Option 1: Upload audio file
audio_file = st.file_uploader("Upload audio question", type=["wav", "mp3"])

# Option 2: Record audio using streamlit-webrtc
# Custom audio processor
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.recorded_frames = []

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        pcm = frame.to_ndarray(format="s16")
        self.recorded_frames.append(pcm)
        return frame

audio_processor_instance = AudioProcessor()

webrtc_ctx = webrtc_streamer(
    key="audio-recorder",
    mode="sendrecv",
    audio_receiver_size=1024,
    media_stream_constraints={"audio": True, "video": False},
    audio_processor_factory=lambda: audio_processor_instance,
    async_processing=True,
)

filename = None

def save_audio(frames, sample_rate=48000):
    audio = np.concatenate(frames, axis=1).T
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    sf.write(temp_file.name, audio, sample_rate)
    return temp_file.name

if audio_file is not None:
    filename = f"temp_{uuid.uuid4().hex}.{audio_file.name.split('.')[-1]}"
    with open(filename, "wb") as f:
        f.write(audio_file.read())
    st.audio(filename)

elif webrtc_ctx.state.playing:
    if audio_processor_instance.recorded_frames:
        filename = save_audio(audio_processor_instance.recorded_frames)
        st.audio(filename)

if filename is not None:
    with open(filename, "rb") as f:
        try:
            response = requests.post(
                "http://localhost:8005/brief",  # Change this URL if deploying
                files={"audio": (filename, f)},
            )
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Failed to connect to backend: {e}")
            response = None

    # Remove temp file
    if os.path.exists(filename):
        os.remove(filename)

    if response and response.status_code == 200:
        data = response.json()
        st.markdown(f"**🧠 You asked:** `{data['query']}`")
        st.markdown("**📊 Summary:**")
        st.success(data["summary"])

        if os.path.exists("output.mp3"):
            st.markdown("🔊 AI Voice Summary:")
            st.audio("output.mp3", format="audio/mp3")
    elif response:
        st.error(f"❌ Error {response.status_code}: {response.text}")
