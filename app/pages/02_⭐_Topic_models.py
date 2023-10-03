"""Topic models page."""


import os

import streamlit as st
from app.utils.topic_model import fit_model, load_model, restart_topic_model
from app.utils.ui import (
    choose_collection,
    display_vector_db_info,
    init_session_states,
    sidebar_collection_info,
    start_app,
)
from pymilvus import utility

init_session_states()
state = st.session_state
sidebar = st.sidebar

if "app_state" not in state:
    start_app()

st.title("Topic models")

collections = utility.list_collections()
choose_collection(collections=collections, on_change=restart_topic_model)
display_vector_db_info()
st.divider()

sidebar_collection_info()

# if "topic_model" not in state:
sidebar.button("Restart topic model", on_click=restart_topic_model)
# restart_topic_model()

if os.path.exists(f"./cache/{state['collection_name']}/topic_model_docs"):
    st.success(
        "A pre-existing topic model was found in the cache. \n\n"
        "**TIP:** If you have added new papers since the last time you calculated "
        "the topic model, you should recalculate it."
    )
    col1, col2 = st.columns(2)
    col1.button("Load topic model from cache", on_click=load_model)
    col2.button("Recalculate topic model", on_click=fit_model)

else:
    st.info("Fit a topic model to extract the underlying topics in your collection.")
    st.button("Fit topic model", on_click=fit_model)

if state["topic_model_fitted"]:
    st.info(
        "**TIP:** If you fit few topics, is possible your research collections has"
        "few documents. Try adding more papers to get more topics"
    )
    topics = state["topic_model"].topic_model.get_topics()
    st.write("### Topics")
    st.write("The following topics were found in the research collection:")

    st.dataframe(state["topic_model"].topics_info().head(20))
    st.divider()

    st.write("### Topic visualization")

    st.info(
        "**TIPS:** \n\n"
        "- Select an area of the plot to zoom in. \n\n"
        "- Double click on the plot to zoom out. \n\n"
        "- Click a topic in the legend box to hide it. \n\n"
        "- Double click on a topic to hide all others."
    )
    if st.checkbox("See legends on the side", value=False):
        document_viz = state["topic_model"].visualize_documents(hide_annotations=True)
        for i, annotation in enumerate(document_viz.layout.annotations):
            if i % 2 == 0:
                annotation.text = ""
    else:
        document_viz = state["topic_model"].visualize_documents()
        document_viz.update_layout(showlegend=False)
    st.plotly_chart(document_viz, use_container_width=False)

    if st.checkbox("Show topics over time"):
        topics_over_time_viz = state["topic_model"].visualize_over_time()
        st.plotly_chart(topics_over_time_viz, use_container_width=False)
