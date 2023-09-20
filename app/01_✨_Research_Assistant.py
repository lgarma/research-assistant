"""App main page."""

import streamlit as st
from app.utils.utils import download_abstracts
from pymilvus import utility
from streamlit_tags import st_tags
from utils.llm import LabelPapers, get_keyword_suggestions
from utils.ui import init_session_states, reset_app, start_app
from utils.utils import display_recomended_papers

init_session_states()
state = st.session_state
sidebar = st.sidebar
st.write(state)

if state.app_state is None:
    start_app()

st.title("Research Assistant")
st.sidebar.button("Reset app", on_click=reset_app)
st.sidebar.button("Do nothing button")

sidebar.checkbox("Continue previous research?", value=False, key="connect")
if state.connect:
    collections = utility.list_collections()
    collections = sorted([c.replace("_", " ").title() for c in collections])
    collection_name = sidebar.selectbox("Select a collection", options=collections)
    state["collection"] = collection_name.replace(" ", "_").lower()


question = st.text_input(
    "What do you want to research today?",
    value="Recent discoveries made by the JWST?",
    key="question",
)

if st.button("Get suggestions"):
    state["chat_suggestions"] = get_keyword_suggestions(
        question=question, max_results=15
    )

if "chat_suggestions" in state:
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

# The user has pressed the button to get suggestions, and the vector database
# has not been created yet.
if "chat_suggestions" in state and "vector_db" not in state:
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
    similar_docs = state["vector_db"].similarity_search(
        query="Represent this sentence for searching relevant passages:"
        + state["question"],
        k=15,
    )
    papers = [
        {
            "title": doc.metadata["title"],
            "authors": doc.metadata["authors"],
            "published": doc.metadata["published"],
            "abstract": doc.page_content,
            "link": doc.metadata["link"],
        }
        for doc in similar_docs
    ]

    st.write("# Abstracts that could help with your research:")
    tab1, tab2, tab3 = st.tabs(["1-5", "6-10", "11-15"])

    with tab1:
        if "tab1_papers" not in state:
            papers_recomendation = LabelPapers(
                question=state["question"], papers=papers[:5]
            ).get_chat_labels()
            state["tab1_papers"] = papers_recomendation

        display_recomended_papers(
            papers=papers[:5], chat_suggestions=state["tab1_papers"]
        )

    with tab2:
        if "tab2_papers" not in state:
            papers_recomendation = LabelPapers(
                question=state["question"], papers=papers[5:10]
            ).get_chat_labels()
            state["tab2_papers"] = papers_recomendation

        display_recomended_papers(
            papers=papers[5:10], chat_suggestions=state["tab2_papers"]
        )

    with tab3:
        if "tab3_papers" not in state:
            papers_recomendation = LabelPapers(
                question=state["question"], papers=papers[10:15]
            ).get_chat_labels()
            state["tab3_papers"] = papers_recomendation

        display_recomended_papers(
            papers=papers[10:15], chat_suggestions=state["tab3_papers"]
        )
