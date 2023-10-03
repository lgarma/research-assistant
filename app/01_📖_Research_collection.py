"""App main page."""
import random

import streamlit as st
from app.utils.utils import download_abstracts
from app.utils.vector_database import disconnect_from_vector_db
from pymilvus import utility
from streamlit_tags import st_tags
from utils.llm import KeywordsAgent
from utils.ui import (
    choose_collection,
    display_vector_db_info,
    init_session_states,
    sidebar_collection_info,
    start_app,
)

init_session_states()
state = st.session_state
sidebar = st.sidebar

if "app_state" not in state:
    start_app()

st.title("Research Collections")

collections = utility.list_collections()
if len(collections) > 0 and st.checkbox(
    "Continue previous research?", value=False, on_change=disconnect_from_vector_db
):
    choose_collection(collections=collections)
    display_vector_db_info()


st.divider()

st.write("## Build a research collection")
question = st.text_input(
    "What do you want to research today?",
    value="JWST discoveries",
    key="question",
    on_change=disconnect_from_vector_db,
)

if st.button("Generate keywords"):
    state["first_keywords"], state["refined_keywords"] = KeywordsAgent(
        question=question,
        n_exploratory_papers=50,
        sort_by="Relevance",
    )()

more_keywords = st.empty()

if "refined_keywords" in state:
    st.info(
        "These keywords could be useful for your research. "
        "Feel free to edit them as you see fit. "
        "Use the 'Generate new keywords' button to get a new set of suggestions."
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
        st.info(
            f"{state['total_new_documents']} abstracts were downloaded. \n\n"
            "Total abstracts in the collection: "
            f"{state['vector_db'].col.num_entities}"
        )

    state["max_papers"] = cols[1].number_input(
        "Max number of papers to download",
        value=1000,
        min_value=100,
        max_value=3000,
        help="Press enter to update the number of papers to download.",
    )

    state["sort_by"] = cols[1].selectbox("Sort by", ["Relevance", "Submitted date"])
    state["placeholder"] = st.empty()

sidebar_collection_info()


st.divider()

if "vector_db" in state:
    st.write("## Example abstract in the collection:")
    with st.expander("Show example abstract"):
        query = random.choice(
            [
                "science",
                "astronomy",
                "physics",
                "biology",
                "chemistry",
                "mathematics",
                "geology",
                "psychology",
                "sociology",
                "economics",
                "history",
                "philosophy",
                "literature",
                "art",
            ]
        )

        doc = state["vector_db"].similarity_search(
            query=query,
            k=1,
        )
        st.write("Title:", doc[0].metadata["title"])
        st.write("Authors:", doc[0].metadata["authors"])
        st.write("Published:", doc[0].metadata["published"])
        st.write("Link:", doc[0].metadata["link"])
        st.write("Abstract:", doc[0].page_content)

    st.divider()
    st.write("## Explore the collection")
    col1, col2 = st.columns(2)
    col1.success("**Common topics, new trends, and research ideas:**")
    col1.link_button("Explore topics", url="http://localhost:8501/Topic_models")

    col2.success("**Paper recommendations, Question answering:**")
    col2.link_button(
        "Explore collections", url="http://localhost:8501/Explore_collections"
    )
    st.divider()
