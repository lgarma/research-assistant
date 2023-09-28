"""Topic models page."""
import os

import streamlit as st
from app.utils.topic_model import TopicModel
from app.utils.ui import choose_collection
from app.utils.vector_database import display_vector_db_info
from pymilvus import utility

state = st.session_state
st.title("Topic models")
st.sidebar.button("Do nothing button")

collections = utility.list_collections()
choose_collection(collections=collections, use_sidebar=False)

display_vector_db_info()

if st.checkbox("Create topic model for this collection"):
    topic_model = TopicModel()

    if os.path.exists(f"./cache/{state['collection_name']}/topic_model_docs"):
        st.write("Loading topic model from cache...")
        topic_model.load_model()
        state["topic_model_fitted"] = True

    if st.button("Fit topic model"):
        topic_model.fit_model()
        state["topic_model_fitted"] = True

    if state["topic_model_fitted"]:

        topics = topic_model.topic_model.get_topics()
        st.write("### Topics")
        st.write("The following topics were found in the collection:")

        st.dataframe(topic_model.topics_info())

        if st.checkbox("Show documents visualization"):
            document_viz = topic_model.visualize_documents()
            if st.checkbox("Hide legends", value=True):
                document_viz.update_layout(showlegend=False)
            st.plotly_chart(document_viz, use_container_width=True)

        if st.checkbox("Show topics over time"):
            topics_over_time_viz = topic_model.visualize_over_time()
            st.plotly_chart(topics_over_time_viz, use_container_width=True)
