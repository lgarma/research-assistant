"""Vector database utilities."""
import streamlit as st
from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from langchain.vectorstores import Milvus
from pymilvus import connections, utility


def get_vector_db(
    docs: list[Document], collection_name: str, embedding_function: Embeddings
) -> Milvus:
    """Get the Milvus vector database for the documents content.

    If the collection already exists, it is loaded. If not, it is created.

    Parameters:
        docs (list[Document]):
            List of documents to be loaded in the database.

        collection_name (str):
            Name of the collection to connect to.

        embedding_function (Embeddings):
            Embedding function to use to vectorize the documents.
    """
    milvus_connection = {"alias": "default", "host": "localhost", "port": 19530}
    connections.connect(**milvus_connection)
    if utility.has_collection(collection_name):
        st.write("Collection already exists. Loading collection...")
        return Milvus(
            collection_name=collection_name,
            embedding_function=embedding_function,
        )
    else:
        st.write(
            f"Collection does not exist. Creating collection with name"
            f" {collection_name}..."
        )
        return Milvus.from_documents(
            documents=docs,
            embedding=embedding_function,
            connection_args=milvus_connection,
            collection_name=collection_name,
        )
