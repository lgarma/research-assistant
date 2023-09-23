"""Topic model utilities."""
import os

import numpy as np
import streamlit as st
from app.utils.vector_database import get_all_documents
from bertopic import BERTopic
from bertopic.representation import OpenAI
from hdbscan import HDBSCAN
from plotly.graph_objs import Figure
from umap import UMAP

state = st.session_state


class TopicModel:
    """
    A topic model that uses BERTopic to cluster documents and embeddings.

    Parameters:
        hdbscan_params (dict):
            Parameters for the HDBSCAN clustering algorithm.

        umap_params (dict):
            Parameters for the UMAP dimensionality reduction algorithm.

        representation_params (dict):
            Parameters for the OpenAI representation model.

    Attributes:
        topic_model (BERTopic):
            The BERTopic model.
    """

    def __init__(
        self,
        umap_params: dict = None,
        hdbscan_params: dict = None,
        representation_params: dict = None,
    ):
        """
        Initialize the topic model.

        Parameters:
            umap_params (dict):
                Parameters for the UMAP dimensionality reduction algorithm.

            hdbscan_params (dict):
                Parameters for the HDBSCAN clustering algorithm.

            representation_params (dict):
                Parameters for the representation model.
        """
        if umap_params is None:
            umap_params = {
                "n_neighbors": 15,
                "n_components": 5,
                "min_dist": 0.0,
                "metric": "cosine",
                "low_memory": False,
                "random_state": 42,
            }
        if hdbscan_params is None:
            hdbscan_params = {
                "min_cluster_size": 10,
                "metric": "euclidean",
                "cluster_selection_method": "eom",
                "prediction_data": True,
            }

        if representation_params is None:
            representation_params = {
                "model": "gpt-3.5-turbo",
                "chat": True,
                "nr_docs": 3,
                "diversity": 0,
            }

        umap = UMAP(**umap_params)
        hdbscan = HDBSCAN(**hdbscan_params)
        representation = OpenAI(**representation_params)

        if os.path.exists(f"./cache/{state['collection_name']}/topic_model_docs"):
            st.write("Loading pre-existing topic model...")
            self.topic_model = BERTopic.load(
                path=f"./cache/{state['collection_name']}/topic_model_docs",
                embedding_model=state["embedding_model"].model_name,
            )
            self.model_fitted = True
        else:
            st.write("Creating new topic model...")
            self.topic_model = BERTopic(
                embedding_model=state["embedding_model"].model_name,
                umap_model=umap,
                hdbscan_model=hdbscan,
                representation_model=representation,
                # Hyperparameters
                calculate_probabilities=False,
                top_n_words=10,
                n_gram_range=(1, 2),
                verbose=True,
            )
            self.model_fitted = False

        self.documents = get_all_documents()
        self.embeddings = np.array(
            state["cached_embedder"].embed_documents(
                [doc.page_content for doc in self.documents]
            )
        )

    def fit_model(self):
        """Fit a topic model to a set of documents and embeddings."""
        if self.model_fitted:
            st.write("Model already fitted.")
            return
        contents = [doc.page_content for doc in self.documents]
        self.topic_model.fit(
            documents=contents,
            embeddings=self.embeddings,
        )
        self.save_model()

    def save_model(self):
        """Save the topic model."""
        self.topic_model.save(
            path=f"./cache/{state['collection_name']}/" f"topic_model_docs",
            serialization="safetensors",
            save_ctfidf=True,
            save_embedding_model=state["embedding_model"].model_name,
        )

    def visualize_documents(self) -> Figure:
        """Visualize the documents."""
        titles = [doc.metadata["title"] for doc in self.documents]
        reduced_embeddings = UMAP(
            n_neighbors=15,
            n_components=2,
            min_dist=0.0,
            metric="cosine",
            random_state=42,
        ).fit_transform(self.embeddings)

        return self.topic_model.visualize_documents(
            docs=titles,
            embeddings=reduced_embeddings,
            title=state["collection_name"],
        )
