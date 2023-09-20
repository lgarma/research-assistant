"""Utility functions for the app."""
import re

import arxiv
import streamlit as st
from app.utils.vector_database import get_vector_db
from langchain.embeddings import HuggingFaceEmbeddings
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
        st.write("Using big slow client")
    else:
        client = arxiv.Client(page_size=100, delay_seconds=3, num_retries=3)
        st.write("Using small fast client")

    st.write(client)
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
        vector_db = get_vector_db(
            docs=bulk_papers,
            collection_name=clean_string(state["question"]),
            embedding_function=HuggingFaceEmbeddings(
                model_name=state.sentence_model,
                encode_kwargs={"normalize_embeddings": True},
            ),
        )
        state["vector_db"] = vector_db

        st.write("Done!")


def display_recomended_papers(papers: list[dict], chat_suggestions: dict):
    """Display the recommended papers."""
    for i, paper in enumerate(chat_suggestions):

        st.write(f"#### {papers[i]['title']}")
        if paper.score >= 4:
            st.success("Highly recommended for your research")
        st.write(f"Authors: {papers[i]['authors']}")
        st.write(f"Published: {papers[i]['published']}")
        # Add arxiv link
        st.write(f"Link: {papers[i]['link']}")
        st.write(f"Topics: {paper.topics}")
        st.write(f"Score: {paper.score}")
        st.write(f"Reasoning: {paper.reasoning}")
        with st.expander("Show Abstract"):
            st.write(papers[i]["abstract"])
