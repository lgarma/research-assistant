"""Explore collections page."""

import streamlit as st
from app.utils.llm import ScorePapersAgent
from app.utils.ui import (
    choose_collection,
    display_vector_db_info,
    init_session_states,
    start_app,
)
from app.utils.utils import clear_recommendations
from pymilvus import utility

init_session_states()
state = st.session_state
if state.app_state is None:
    start_app()

st.title("Explore collections")

collections = utility.list_collections()
choose_collection(collections=collections, use_sidebar=False)
display_vector_db_info()
st.divider()

st.write("## Get paper recommendations")
st.info("Ask a something and get paper recommendations from the collection.")

state["question"] = st.text_input(
    "Ask something",
    state["nice_collection_name"],
    on_change=clear_recommendations,
)

if st.checkbox("Generate papers recommendations"):

    similar_docs = state["vector_db"].similarity_search(
        query="Represent this sentence for searching relevant passages: "
        + state["question"],
        k=12,
        param={"metric_type": "L2", "params": {"nprobe": 16}},
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

    n_rows = state["rows"]  # starts at 2 rows
    n_cols = 2
    n_papers = 4
    for row in range(n_rows):
        # Start a new batch every n_papers
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
