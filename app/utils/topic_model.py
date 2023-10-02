"""Topic model utilities."""
import datetime

import numpy as np
import pandas as pd
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
                "n_neighbors": 10,
                "n_components": 5,
                "min_dist": 0.0,
                "metric": "cosine",
                "low_memory": False,
                "random_state": 42,
            }
        if hdbscan_params is None:
            hdbscan_params = {
                "min_cluster_size": 15,
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
        self.documents = get_all_documents()
        self.embeddings = np.array(
            state["cached_embedder"].embed_documents(
                [doc.page_content for doc in self.documents]
            )
        )

    def fit_model(self):
        """Fit a topic model to a set of documents and embeddings."""
        self.__init__()
        contents = [doc.page_content for doc in self.documents]
        self.topic_model.fit(
            documents=contents,
            embeddings=self.embeddings,
        )
        self.save_model()
        state["topic_model_fitted"] = True

    def save_model(self):
        """Save the topic model."""
        self.topic_model.save(
            path=f"./cache/{state['collection_name']}/" f"topic_model_docs",
            serialization="safetensors",
            save_ctfidf=True,
            save_embedding_model=state["embedding_model"].model_name,
        )

    def visualize_documents(self, hide_annotations=False) -> Figure:
        """Visualize the documents."""
        hover = []
        for doc in self.documents:
            title = f"{doc.metadata['title']}<br>"
            # divide authors in lines of 6 authors
            authors_list = doc.metadata["authors"].split(",")
            authors = ""
            for i, author in enumerate(authors_list):
                authors += f"{author}"
                authors += (
                    "<br>"
                    if (i % 5 == 0 and i != 0) or i == len(authors_list) - 1
                    else ", "
                )
            published = f"{doc.metadata['published']}<br>"
            hover.append(title + authors + published)

        reduced_embeddings = UMAP(
            n_neighbors=15,
            n_components=2,
            min_dist=0.0,
            metric="cosine",
            random_state=42,
        ).fit_transform(self.embeddings)

        self.get_custom_labels()
        return self.topic_model.visualize_documents(
            docs=hover,
            reduced_embeddings=reduced_embeddings,
            title=f'<b> {state["nice_collection_name"]} </b>',
            custom_labels=True,
            hide_annotations=hide_annotations,
        )

    def get_custom_labels(self):
        """Get custom labels for the topics for simplified visualization."""

        def get_first_words(s: str, n: int):
            """Get the first n words of a string."""
            words = s.split(" ")
            return " ".join(words[:n])

        topics = self.topic_model.get_topics()

        custom_labels = [
            f"{get_first_words(topics[topic][0][0], 5)} ..." for topic in topics
        ]
        self.topic_model.set_topic_labels(custom_labels)

    def load_model(self):
        """Load a pre-existing topic model."""
        st.write("Loading pre-existing topic model from cache...")
        self.topic_model = BERTopic.load(
            path=f"./cache/{state['collection_name']}/topic_model_docs",
            embedding_model=state["embedding_model"].model_name,
        )
        state["topic_model_fitted"] = True

    def visualize_over_time(self):
        """Visualize the topics over time."""
        timestamps = [
            datetime.datetime(doc.metadata["published"], 1, 1) for doc in self.documents
        ]
        contents = [doc.metadata["title"] for doc in self.documents]
        topics_over_time = self.topic_model.topics_over_time(
            contents,
            timestamps,
        )
        return self.topic_model.visualize_topics_over_time(
            topics_over_time,
            top_n_topics=10,
        )

    def topics_info(self) -> pd.DataFrame:
        """Get a dataframe with the topics and their metadata."""
        topic_info = self.topic_model.get_topic_info()
        df = topic_info[["Count", "Representation"]]

        def convert_to_string(lst):
            """Convert a list to a string."""
            return " ".join(lst)

        df["Representation"] = df["Representation"].apply(convert_to_string)
        return df.iloc[range(1, len(df))]


def restart_topic_model():
    """Restart the topic model."""
    del state["topic_model"]
    state["topic_model_fitted"] = False
