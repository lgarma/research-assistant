"""Topic models page."""

import streamlit as st
from app.utils.topic_model import TopicModel
from app.utils.vector_database import connect_to_vector_db
from pymilvus import utility

st.title("Topic models")
state = st.session_state

st.button("Do nothing button")
st.write(state)

collections = utility.list_collections()
collections = sorted([c.replace("_", " ").title() for c in collections])
collection_name = st.selectbox("Select a research collection", options=collections)

collection_name = collection_name.replace(" ", "_").lower()
state["collection_name"] = collection_name

if st.button("Create topic model"):
    connect_to_vector_db()

    topic_model = TopicModel()
    st.write(f"Documents: {len(topic_model.documents)}")

    topic_model.fit_model()
    document_viz = topic_model.visualize_documents()

    st.plotly_chart(document_viz)
