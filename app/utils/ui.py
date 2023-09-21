"""UI utilities for the app."""

import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import HuggingFaceEmbeddings
from pymilvus import connections


def set_state_if_absent(key, value):
    """Set the state if it is absent."""
    if key not in st.session_state:
        st.session_state[key] = value


def init_session_states():
    """Initialize the app."""
    set_state_if_absent(
        key="chat", value=ChatOpenAI(model="gpt-3.5-turbo", temperature=0.01)
    )
    set_state_if_absent(key="app_state", value=None)
    set_state_if_absent(key="rows", value=2)
    set_state_if_absent(
        key="embedding_model",
        value=HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en", encode_kwargs={"normalize_embeddings": True}
        ),
    )


def start_app():
    """Start the app."""
    st.session_state.app_state = "initialized"
    milvus_connection = {"alias": "default", "host": "localhost", "port": 19530}
    connections.connect(**milvus_connection)


def reset_app():
    """Reset the app."""
    for key in st.session_state:
        del st.session_state[key]
    init_session_states()
