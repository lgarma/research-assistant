"""App main page."""

import streamlit as st
from utils.llm import get_keyword_suggestions
from utils.ui import init_app

init_app()


st.title("Research Assistant")
st.write("What do you want to research today?")
question = st.text_input(
    "Question", value="Ask a question here...", help="How do spiral arms form?"
)

st.button("Run", key="run")

if st.session_state.run:
    chat_suggestions = get_keyword_suggestions(question=question)
    st.write(chat_suggestions)
    st.write("The following keywords could be useful for your research:")
    st.multiselect(
        label="Relevant Keywords",
        options=chat_suggestions["keywords"].split(", "),
        default=chat_suggestions["keywords"].split(", "),
    )
    st.write(f"Similar questions: {chat_suggestions['similar questions']}")
