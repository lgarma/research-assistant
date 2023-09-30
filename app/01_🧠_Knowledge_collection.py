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
    start_app,
)

init_session_states()
state = st.session_state
sidebar = st.sidebar

if state.app_state is None:
    start_app()

st.title("Research Assistant")
# st.sidebar.button("Reset app", on_click=reset_app)
# st.sidebar.button("Do nothing button")


collections = utility.list_collections()
if len(collections) > 0 and st.checkbox(
    "Continue previous research?", value=False, on_change=disconnect_from_vector_db
):
    choose_collection(collections=collections)
    display_vector_db_info()


st.divider()

st.write("## Search Arxiv abstracts")
if "collection_name" in state:
    info = (
        "Abstracts will be saved in the "
        f"**'{state['nice_collection_name']}'** collection."
    )
else:
    info = (
        "Abstracts will be saved in a new collection named after your research "
        "question."
    )

st.info(info)
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
        value=100,
        min_value=10,
        max_value=2000,
    )
    state["placeholder"] = st.empty()
    st.write("---")

    if state["vector_db"].col.num_entities > 0:
        st.info("Explore the collection in the **'Explore collections'** tab.")
        st.link_button(
            "Explore collections", url="http://localhost:8501/Explore_collections"
        )
        st.divider()

        with st.expander("Example abstract in the collection"):
            doc = state["vector_db"].similarity_search(
                query="science",
                k=1,
            )
            st.write("Title:", doc[0].metadata["title"])
            st.write("Authors:", doc[0].metadata["authors"])
            st.write("Published:", doc[0].metadata["published"])
            st.write("Link:", doc[0].metadata["link"])
            st.write("Abstract:", doc[0].page_content)
