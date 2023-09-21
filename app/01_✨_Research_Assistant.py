"""App main page."""

import streamlit as st
from app.utils.utils import download_abstracts
from app.utils.vector_database import connect_to_vector_db
from pymilvus import utility
from streamlit_tags import st_tags
from utils.llm import LabelPapers, get_keyword_suggestions
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
st.write(collections)
if len(collections) > 0 and sidebar.checkbox(
    "Continue previous research?", value=False
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
)

if st.button("Get keyword suggestions"):
    state["chat_suggestions"] = get_keyword_suggestions(
        question=question, max_results=15
    )

if "chat_suggestions" in state:
    st.write("### Suggested keywords:")
    st.info(
        "These keywords could be useful for searching papers in arxiv. "
        "Feel free to add or remove keywords as you see fit. "
        "Press the button to download abstracts from arxiv using these keywords."
    )
    keywords = st_tags(
        label="",
        text="Press enter to add more",
        value=state["chat_suggestions"]["keywords"].split(", "),
    )


if "chat_suggestions" in state:
    cols = st.columns(2)
    cols[0].button(
        "Search keywords in Arxiv", key="search_arxiv", on_click=download_abstracts
    )
    cols[1].number_input(
        "Max number of papers to download",
        value=100,
        min_value=10,
        max_value=2000,
        key="max_results",
    )
    state["placeholder"] = st.empty()
    st.write("---")


if "vector_db" in state and st.button("Get Chat suggestions"):
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
        if row * n_cols % n_papers == 0 and f"row{row}" not in state:
            chat_labels = LabelPapers(
                question=state["question"],
                papers=papers[row * n_cols : row * n_cols + n_papers],
            ).get_chat_labels()
            state[f"batch{row*n_cols/n_papers}"] = chat_labels
        chat_labels = state[f"row{row*n_cols//n_papers}"]

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
    if st.button("Show more"):
        state["rows"] += 2
