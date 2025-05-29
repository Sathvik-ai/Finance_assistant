import streamlit as st
import requests
import uuid
import os
import tempfile
import numpy as np
import av
import spacy
from scipy.io.wavfile import write as wav_write
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase

# Page config
st.set_page_config(page_title="Finance Assistant", layout="centered")
st.title("🎙️ Voice-Driven Market Brief Assistant")

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Upload option
st.markdown("### 🎧 Upload `.wav` or `.mp3` **or record using microphone**")
audio_file = st.file_uploader("Upload audio question", type=["wav", "mp3"])

# AudioProcessor class
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.frames = []

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        self.frames.append(frame.to_ndarray(format="s16"))
        return frame

# Start webrtc recording
webrtc_ctx = webrtc_streamer(
    key="recorder",
    mode="sendrecv",
    media_stream_constraints={"audio": True, "video": False},
    audio_receiver_size=1024,
    audio_processor_factory=lambda: AudioProcessor(),
    async_processing=True,
)

# Save audio
def save_audio(frames, rate=48000):
    audio = np.concatenate(frames, axis=1).T
    audio = (audio * 32767).astype(np.int16) if audio.dtype != np.int16 else audio
    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wav_write(temp_wav.name, rate, audio)
    return temp_wav.name

filename = None

# Uploaded file path
if audio_file is not None:
    filename = f"temp_{uuid.uuid4().hex}.{audio_file.name.split('.')[-1]}"
    with open(filename, "wb") as f:
        f.write(audio_file.read())
    st.audio(filename)

# Recorded audio path
elif webrtc_ctx and webrtc_ctx.state.playing:
    processor = webrtc_ctx.audio_processor
    if processor and hasattr(processor, "frames") and processor.frames:
        filename = save_audio(processor.frames)
        st.audio(filename)

# Send to backend
if filename:
    with open(filename, "rb") as f:
        try:
            response = requests.post(
                "http://localhost:8005/brief",
                files={"audio": (filename, f)},
            )
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Backend error: {e}")
            response = None

    os.remove(filename)

    if response and response.status_code == 200:
        result = response.json()
        st.markdown(f"**🧠 Query:** `{result['query']}`")
        st.markdown("**📊 Summary:**")
        st.success(result["summary"])

        if os.path.exists("output.mp3"):
            st.markdown("🔊 AI Voice Summary:")
            st.audio("output.mp3", format="audio/mp3")
    elif response:
        st.error(f"❌ Error {response.status_code}: {response.text}")
