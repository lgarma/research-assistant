"""Utility functions for the app."""

import streamlit as st
from app.utils.utils import get_arxiv_abstracts
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.output_parsers.pydantic import PydanticOutputParser
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.prompts.chat import AIMessage
from pydantic import BaseModel, Field


def get_response_schema_for_keywords():
    """Get response schema for keywords."""
    return [
        ResponseSchema(
            name="categories",
            description="Categories that could be useful for the user "
            "research. Use the arxiv category taxonomy. ",
        ),
        ResponseSchema(
            name="related questions",
            description="List questions that the user might also want to research. "
            "Separate the questions with a comma.",
        ),
        ResponseSchema(
            name="keywords",
            description="List relevant keywords that could be useful "
            "for the user research. Be specific. "
            "Do not use keywords that could be used in other fields. "
            "(for example 'science' or 'challenges' are too general ). "
            "These keywords will be used to search for papers in arxiv. ",
        ),
    ]


def get_chat_keyword_suggestions(question: str) -> dict:
    """Initial prompt of the app. Ask the user what they want to research.

    Return dictionary with arxiv categories, keywords, similar questions and
    sorting criteria.
    """
    response_schemas = get_response_schema_for_keywords()
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()

    prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(
                "Help the user with their research as best as possible. "
                "\n{format_instructions}"
            ),
            HumanMessagePromptTemplate.from_template("I want to research: {question}"),
        ],
        input_variables=["question"],
        partial_variables={"format_instructions": format_instructions},
    )

    _input = prompt.format_prompt(question=question)
    output = st.session_state.chat(_input.to_messages())
    return output_parser.parse(output.content)


def refine_keywords(question: str, keywords: list[str], papers: list[str]) -> dict:
    """Using the keywords suggested by Chat, see the top 5 results from arxiv.

    Ask Chat to refine the keywords if necessary.
    """
    response_schemas = get_response_schema_for_keywords()
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()

    prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(
                "Help the user with their research as best as possible. "
                "\n{format_instructions}"
            ),
            HumanMessagePromptTemplate.from_template(
                "I want to research: {question}. "
                "The following are some titles that were downloaded from arxiv using "
                "these keywords: {keywords}. "
                "Use this information, to refine the list of keywords. "
                "Keep the number of keywords small, no more than 10. "
                "Papers: {papers}. "
            ),
        ],
        input_variables=["question", "keywords", "papers"],
        partial_variables={"format_instructions": format_instructions},
    )

    _input = prompt.format_prompt(question=question, keywords=keywords, papers=papers)
    output = st.session_state.chat(_input.to_messages())
    return output_parser.parse(output.content)


def get_keyword_suggestions(question: str):
    """Get keyword suggestions from Chat.

    Uses chat to generate a list of keywords that could be useful for the user research.
    Then downloads the top 10 papers from arxiv using these keywords
    Finally, asks Chat to refine the list of keywords, by looking at the top 10 papers.

    Returns a dictionary with the keywords, categories and related questions.
    """
    first_suggestion = get_chat_keyword_suggestions(question=question)

    top_papers = get_arxiv_abstracts(query=first_suggestion["keywords"], max_results=10)

    top_papers = [
        paper.metadata["title"] + ", " + str(paper.metadata["published"])
        for paper in top_papers
    ]

    refined_suggestions = refine_keywords(
        question=question, keywords=first_suggestion["keywords"], papers=top_papers
    )

    st.session_state["first_suggestion"] = first_suggestion["keywords"]
    return refined_suggestions


class LabelPapers:
    """Label tha papers using an LLM"""

    def __init__(self, question: str, papers: list[dict]):
        """Initialize the LabelChat."""
        self.question = question
        self.papers = papers
        self.output_parser = None

    @staticmethod
    def get_parser():
        """Get the parser for the LLM output."""

        class Papers(BaseModel):
            title: str = Field(description="paper title")
            topics: list = Field(description="Topics that best describe the paper.")
            score: int = Field(
                description="Rate from 1 to 5 how relevant is the paper "
                "for the user research. 5 is a must read, "
                "1 is irrelevant"
            )
            reasoning: str = Field(description="short explanation for the score")

        return PydanticOutputParser(pydantic_object=Papers)

    @staticmethod
    def _get_format_instructions():
        """Response schema for the LLM"""
        response_schemas = [
            ResponseSchema(name="title", description="Paper title"),
            ResponseSchema(
                name="topics",
                description="Topics that best describe the paper.",
                type="list",
            ),
            ResponseSchema(
                name="score",
                description="Rate from 1 to 5 how relevant is the paper "
                "for the user research. 5 is a must read, 1 is irrelevant",
                type="int",
            ),
            ResponseSchema(
                name="reasoning", description="short explanation for the score"
            ),
        ]
        json_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        format_instructions = json_parser.get_format_instructions()

        format_instructions += (
            "\n\nIf the user provides multiple papers, "
            "use a separate the markdown snippets using a divider "
            "'---' "
        )
        return format_instructions

    def get_chat_labels(self):
        """Ask chatgpt to label the papers"""
        format_instruction = self._get_format_instructions()
        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    "Help the user with their research as best as possible. "
                    "\n{format_instruction}"
                ),
                HumanMessagePromptTemplate.from_template(
                    "I want to research: {question}. \n\n"
                    "Here are some papers I downloaded from arxiv. "
                    "All of them are semantically close to my research, "
                    "however, I dont have the time to read them all. "
                    "Using the title, abstract and the published time, "
                    "help me indentify the most relevant papers for my research. "
                    "\n\n"
                    "{papers}"
                ),
            ],
            input_variables=["question", "papers"],
            partial_variables={"format_instruction": format_instruction},
        )
        _input = prompt.format_prompt(
            question=self.question,
            papers=self.papers,
        )

        output = st.session_state.chat(_input.to_messages())
        return self.parse_output(output)

    def parse_output(self, output: AIMessage) -> list[dict]:
        """Use output parser to parse the output"""
        pydantic_parser = self.get_parser()
        split = output.content.split("---")
        return [pydantic_parser.parse(s) for s in split]
