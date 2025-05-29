import streamlit as st
import requests
import uuid
import os
import spacy
import tempfile
import numpy as np
import av
from scipy.io.wavfile import write  # safer than soundfile for deployment
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase

# Page configuration
st.set_page_config(page_title="Finance Assistant", layout="centered")
st.title("🎙️ Voice-Driven Market Brief Assistant")

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

st.markdown("### 🎧 Upload `.wav` or `.mp3` **or record your question using your microphone**")

# Option 1: Upload audio file
audio_file = st.file_uploader("Upload audio question", type=["wav", "mp3"])

# Option 2: Record audio using streamlit-webrtc
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.recorded_frames = []

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        pcm = frame.to_ndarray(format="s16")
        self.recorded_frames.append(pcm)
        return frame

webrtc_ctx = webrtc_streamer(
    key="audio-recorder",
    mode="sendrecv",
    audio_receiver_size=1024,
    media_stream_constraints={"audio": True, "video": False},
    audio_processor_factory=lambda: AudioProcessor(),
    async_processing=True,
)

# Helper function to save audio to a temp file
def save_audio(frames, sample_rate=48000):
    audio = np.concatenate(frames, axis=1).T
    audio = (audio * 32767).astype(np.int16)  # Convert to 16-bit PCM
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    write(temp_file.name, sample_rate, audio)
    return temp_file.name

filename = None

# Process uploaded file
if audio_file is not None:
    filename = f"temp_{uuid.uuid4().hex}.{audio_file.name.split('.')[-1]}"
    with open(filename, "wb") as f:
        f.write(audio_file.read())
    st.audio(filename)

# Process recorded file
elif webrtc_ctx and webrtc_ctx.state.playing:
    processor = webrtc_ctx.audio_processor
    if processor and processor.recorded_frames:
        filename = save_audio(processor.recorded_frames)
        st.audio(filename)

# If file is ready, send to backend
if filename is not None:
    with open(filename, "rb") as f:
        try:
            response = requests.post(
                "http://localhost:8005/brief",  # Replace with your deployed API URL
                files={"audio": (filename, f)},
            )
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Failed to connect to backend: {e}")
            response = None

    # Clean up temporary file
    if os.path.exists(filename):
        os.remove(filename)

    # Handle backend response
    if response and response.status_code == 200:
        data = response.json()
        st.markdown(f"**🧠 You asked:** `{data['query']}`")
        st.markdown("**📊 Summary:**")
        st.success(data["summary"])

        # Play generated audio summary (output.mp3)
        if os.path.exists("output.mp3"):
            st.markdown("🔊 AI Voice Summary:")
            st.audio("output.mp3", format="audio/mp3")
    elif response:
        st.error(f"❌ Error {response.status_code}: {response.text}")
