"""App main page."""

import streamlit as st
from app.utils.utils import download_abstracts
from streamlit_tags import st_tags
from utils.llm import get_keyword_suggestions
from utils.ui import init_session_states, reset_app, start_app

init_session_states()
state = st.session_state
sidebar = st.sidebar
st.write(state)

if state.app_state is None:
    start_app()


st.title("Research Assistant")
st.sidebar.button("Reset app", on_click=reset_app)
st.sidebar.button("Do nothing button")
st.write("What do you want to research today?")
question = st.text_input(
    "What do you want to research today?",
    value="Recent discoveries made by the JWST?",
    key="question",
)

if st.button("Get suggestions"):
    state["chat_suggestions"] = get_keyword_suggestions(question)

if "chat_suggestions" in state and "vector_db" not in state:
    st.write("### Suggested keywords:")
    st.info(
        "These keywords could be useful for searching papers in arxiv. "
        "Feel free to add or remove keywords as you see fit. "
        "Then press the button to download some abstracts in arxiv."
    )
    keywords = st_tags(
        label="",
        text="Press enter to add more",
        value=state["chat_suggestions"]["keywords"].split(", "),
    )

    sidebar.number_input(
        "Max number of papers to download",
        value=50,
        min_value=10,
        max_value=1000,
        key="max_results",
    )

    state.placeholder = st.empty()
    st.button(
        "Search keywords in Arxiv", key="search_arxiv", on_click=download_abstracts
    )

if "vector_db" in state:
    st.write("# Abstracts that could help with your research:")

    similar_docs = state["vector_db"].similarity_search(
        query=state["question"],
        k=4,
    )

    for doc in similar_docs:
        st.write(f'### {doc.metadata["title"]}')
        st.write(doc.metadata["authors"])
        st.write(f'Year: {doc.metadata["published"]}')
        st.write(doc.page_content)
        st.write(f'Link: {doc.metadata["link"]}')
