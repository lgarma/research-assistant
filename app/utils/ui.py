"""UI utilities for the app."""

import streamlit as st
from langchain.chat_models import ChatOpenAI


def set_state_if_absent(key, value):
    """Set the state if it is absent."""
    if key not in st.session_state:
        st.session_state[key] = value


def init_app():
    """Initialize the app."""
    set_state_if_absent(key="chat", value=ChatOpenAI(model="gpt-3.5-turbo"))
    set_state_if_absent(key="question", value="How do spiral arms form?")
    set_state_if_absent(key="sentence_model", value="multi-qa-mpnet-base-dot-v1")
    set_state_if_absent(key="app_state", value="initialized")
