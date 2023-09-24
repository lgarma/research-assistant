"""UI utilities for the app."""

import langchain
import streamlit as st
from langchain.cache import SQLiteCache
from langchain.embeddings import HuggingFaceEmbeddings
from pymilvus import connections

state = st.session_state


def set_state_if_absent(key, value):
    """Set the state if it is absent."""
    if key not in state:
        state[key] = value


def init_session_states():
    """Initialize the app."""
    set_state_if_absent(key="app_state", value=None)
    set_state_if_absent(key="rows", value=2)
    set_state_if_absent(
        key="embedding_model",
        value=HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en", encode_kwargs={"normalize_embeddings": True}
        ),
    )


def start_app():
    """Start the app.

    Connect to Milvus and initialize the llm cache.
    """
    langchain.llm_cache = SQLiteCache(database_path=".app.db")
    milvus_connection = {"alias": "default", "host": "localhost", "port": 19530}
    connections.connect(**milvus_connection)
    state.app_state = "initialized"


def reset_app():
    """Reset the app."""
    for key in state:
        del state[key]
    init_session_states()
