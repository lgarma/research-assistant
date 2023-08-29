"""Vector database utilities."""

from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.schema import Document
from langchain.vectorstores import Milvus


def get_embeddings(docs: list[Document]) -> list[list[float]]:
    """Get embeddings for the documents content."""
    embedder = SentenceTransformerEmbeddings(model_name="multi-qa-mpnet-base-dot-v1")
    contents = [doc.page_content for doc in docs]
    return embedder.embed_documents(contents)


def get_vector_db(docs: list[Document]) -> Milvus:
    """Get vector database for the documents content."""
    embeddings = get_embeddings(docs)
    return Milvus.from_documents(
        docs,
        embeddings,
        connection_args={"host": "127.0.0.1", "port": "19530"},
        collection_name="arxiv_papers",
    )
