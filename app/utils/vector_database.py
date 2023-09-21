"""Vector database utilities."""
import streamlit as st
from langchain.embeddings.cache import CacheBackedEmbeddings, _create_key_encoder
from langchain.schema import Document
from langchain.storage import LocalFileStore
from langchain.vectorstores import Milvus


def connect_to_vector_db():
    """Connect to pre-existing vector database.

    Sets up a cached embedder to save the embeddings
    The cached documents can be checked for duplicated documents.
    """
    state = st.session_state
    state["cache"] = LocalFileStore(f"./cache/{state['collection_name']}")
    state["cached_embedder"] = CacheBackedEmbeddings.from_bytes_store(
        underlying_embeddings=state["embedding_model"],
        document_embedding_cache=state["cache"],
        namespace=state["collection_name"],
    )
    state["vector_db"] = Milvus(
        collection_name=state["collection_name"],
        embedding_function=state["cached_embedder"],
    )


def cache_documents_embeddings(docs: list[Document]):
    """Get the embeddings for the documents and cache them.

    Checks for duplicates before caching.
    Returns list of documents that were not in the database.
    """
    state = st.session_state
    new_docs = check_for_duplicates(docs)
    if len(new_docs) > 0:
        st.write(f"Encoding {len(new_docs)} new documents.")
        state["cached_embedder"].embed_documents([doc.page_content for doc in new_docs])
    return new_docs


def check_for_duplicates(docs: list[Document]):
    """Only return documents that where not in the database.

    Extract the uuid of the documents. If the uuid is not in the database, return
    the document.
    """
    state = st.session_state
    # encoder used by langchain
    key_encoder = _create_key_encoder(namespace=state["collection_name"])
    keys = [key_encoder(doc.page_content) for doc in docs]
    preexisting_keys = list(state["cache"].yield_keys())
    return [doc for doc, key in zip(docs, keys) if key not in preexisting_keys]
