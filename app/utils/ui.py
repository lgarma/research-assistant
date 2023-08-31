"""UI utilities for the app."""

import streamlit as st
from langchain.chat_models import ChatOpenAI


def set_state_if_absent(key, value):
    """Set the state if it is absent."""
    if key not in st.session_state:
        st.session_state[key] = value


def init_session_states():
    """Initialize the app."""
    set_state_if_absent(key="chat", value=ChatOpenAI(model="gpt-3.5-turbo"))
    set_state_if_absent(key="sentence_model", value="BAAI/bge-small-en")
    set_state_if_absent(key="app_state", value=None)
    set_state_if_absent(key="suggested_keywords", value=None)


def start_app():
    """Start the app."""
    st.session_state.app_state = "initialized"


def reset_app():
    """Reset the app."""
    for key in st.session_state:
        del st.session_state[key]
    init_session_states()
