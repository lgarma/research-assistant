"""App main page."""

import streamlit as st
from streamlit_tags import st_tags
from utils.llm import get_keyword_suggestions
from utils.ui import init_app, reset_app
from utils.utils import get_arxiv_documents
from utils.vector_database import get_embeddings

if st.session_state.app_state != "initialized":
    init_app()


state = st.session_state
st.title("Research Assistant")
st.sidebar.button("Reset app", on_click=reset_app)
st.sidebar.button("Do nothing button")
st.write("What do you want to research today?")
question = st.text_input(
    "What do you want to research today?",
    value="Recent discoveries made by the JWST?",
)

if st.button("Get suggestions"):
    state["keyword_suggestions"] = get_keyword_suggestions(question)

st.divider()

if "keyword_suggestions" in state:
    st.write("### Related questions:")
    for i, question in enumerate(
        state["keyword_suggestions"]["related questions"].split(", ")
    ):
        st.write(f"- {question}")
        if i == 2:
            break

    st.write("### Suggested keywords:")
    keywords = st_tags(
        label="",
        text="Press enter to add more",
        value=state["keyword_suggestions"]["keywords"].split(", "),
    )

    st.button("Download abstracts")
    with st.status("Downloading abstracts...", expanded=True):
        st.write("Downloading abstracts...")
        bulk_papers = get_arxiv_documents(
            query=state["keyword_suggestions"]["keywords"],
            max_results=500,
        )
        st.write("Extracting embeddings...")
        embeddings = get_embeddings(bulk_papers)

        st.write("Done!")
