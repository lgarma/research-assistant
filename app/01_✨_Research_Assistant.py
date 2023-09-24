"""App main page."""
import random

import streamlit as st
from app.utils.utils import download_abstracts
from app.utils.vector_database import (
    connect_to_vector_db,
    disconnect_from_vector_db,
    display_vector_db_info,
)
from pymilvus import utility
from streamlit_tags import st_tags
from utils.llm import KeywordsAgent, ScorePapersAgent
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


collections = utility.list_collections()
if len(collections) > 0 and sidebar.checkbox(
    "Continue previous research?", value=False, on_change=disconnect_from_vector_db
):
    collections = sorted([c.replace("_", " ").title() for c in collections])
    collection_name = sidebar.selectbox("Select a collection", options=collections)
    collection_name = collection_name.replace(" ", "_").lower()
    state["collection_name"] = collection_name
    connect_to_vector_db()


question = st.text_input(
    "What do you want to research today?",
    value="Recent discoveries made by the JWST?",
    key="question",
    on_change=disconnect_from_vector_db,
)

if st.button("Generate keyword suggestions"):
    state["first_keywords"], state["refined_keywords"] = KeywordsAgent(
        question=question,
        n_exploratory_papers=30,
    )()

more_keywords = st.empty()

if "refined_keywords" in state:
    st.info(
        "These keywords could be useful for your research. "
        "Add or remove them as you see fit. "
        "If you want to generate a new set of keywords, "
        "use the button below."
    )
    keywords = st_tags(
        label="",
        text="Press enter to add more",
        value=state["refined_keywords"][:10],
    )

if "refined_keywords" in state:
    cols = st.columns(2)
    if cols[0].button("Generate new keywords", key="new_keywords"):
        random.shuffle(state["refined_keywords"])
        st.experimental_rerun()

    if cols[0].button("Search abstracts in Arxiv with these keywords"):
        download_abstracts()

    state["max_papers"] = cols[1].number_input(
        "Max number of papers to download",
        value=100,
        min_value=10,
        max_value=2000,
    )
    state["placeholder"] = st.empty()
    st.write("---")

display_vector_db_info()
if "vector_db" in state and st.checkbox("Generate papers recommendations?"):
    similar_docs = state["vector_db"].similarity_search(
        query="Represent this sentence for searching relevant passages:"
        + state["question"],
        k=16,
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

    n_rows = state["rows"]  # starts with 4 rows
    n_cols = 2
    n_papers = 4
    for row in range(n_rows):
        # Label batch of n_papers
        if row * n_cols % n_papers == 0 and f"batch{row*n_cols//n_papers}" not in state:
            chat_labels = ScorePapersAgent(
                question=state["question"],
                papers=papers[row * n_cols : row * n_cols + n_papers],
            ).get_chat_labels()
            state[f"batch{row*n_cols//n_papers}"] = chat_labels
        chat_labels = state[f"batch{row*n_cols//n_papers}"]

        st.write("---")
        cols = st.columns(n_cols, gap="large")
        for col in range(n_cols):
            i = row * n_cols + col
            with cols[col]:
                labels = chat_labels[i % n_papers]
                st.markdown(f"#### {papers[i]['title']}")
                if labels.score >= 4:
                    st.success("Highly recommended for your research")
                st.markdown(f"**{papers[i]['authors']}**")
                st.markdown(f"*{papers[i]['published']}*")
                st.markdown(f"*{papers[i]['link']}*")
                st.caption(f"Topics: {', '.join(labels.topics)}")
                st.markdown(f"Score: {labels.score}")
                st.markdown(f"**Reasoning**: {labels.reasoning}")
                with st.expander("Show Abstract"):
                    st.write(papers[i]["abstract"])

    st.write("---")
    if st.button("Generate more recommendations"):
        state["rows"] += 2
        st.experimental_rerun()
