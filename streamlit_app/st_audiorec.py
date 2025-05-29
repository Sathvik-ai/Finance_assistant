import streamlit as st
import numpy as np
from streamlit.components.v1 import declare_component
import os

# Use the local path to the component
component_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "streamlit_audio_recorder"))
_st_audiorec = declare_component("st_audiorec", path=component_path)

def st_audiorec():
    audio_data = _st_audiorec()
    if audio_data is None:
        return None
    else:
        return np.array(audio_data, dtype=np.uint8)
