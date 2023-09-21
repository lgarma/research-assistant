"""Utility functions for the app."""
import re

import arxiv
import streamlit as st
from app.utils.vector_database import get_vector_db
from langchain.schema import Document


def clean_string(input_string: str) -> str:
    """Remove special characters, replace spaces with underscores, and lowercase."""
    cleaned_string = re.sub(r"[^\w\s]", "", input_string)
    cleaned_string = cleaned_string.replace(" ", "_")
    return cleaned_string.lower()


def get_arxiv_abstracts(
    query: str, sort_by: str = "Relevance", max_results=5
) -> list[Document]:
    """Get arxiv abstracts using the query.

    Saves them in a list of Document objects. Keeps the title, authors, link, journal
    and comment as metadata.
    """
    # If the request is too big, we need to use a slower client
    if max_results > 500:
        client = arxiv.Client(page_size=500, delay_seconds=5, num_retries=7)
    else:
        client = arxiv.Client(page_size=100, delay_seconds=3, num_retries=3)

    results = client.results(
        arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
            if sort_by == "Relevance"
            else arxiv.SortCriterion.SubmittedDate,
        )
    )
    docs = []
    for i, result in enumerate(results):
        try:
            docs.append(
                Document(
                    page_content=result.summary,
                    metadata={
                        "published": result.published.year,
                        "title": result.title,
                        "authors": ", ".join(
                            [author.name for author in result.authors]
                        ),
                        "link": result.entry_id,
                    },
                )
            )
        except Exception as e:
            st.write(f"Error: {e}", i)
    return docs


def download_abstracts():
    """Download abstracts from arxiv and store them in a milvus collection database.

    The collection name is the cleaned question string.
    """
    state = st.session_state
    with state.placeholder.status("Downloading abstracts...", expanded=False):
        st.write("Downloading abstracts...")
        bulk_papers = get_arxiv_abstracts(
            query=state["chat_suggestions"]["keywords"],
            max_results=state["max_results"],
        )
        st.write("Storing documents in vectorstore...")
        st.write(state["embedding_model"])
        vector_db = get_vector_db(
            docs=bulk_papers,
            collection_name=clean_string(state["question"]),
            embedding_function=state["embedding_model"],
        )
        state["vector_db"] = vector_db

        st.write("Done!")
