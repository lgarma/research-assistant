"""Utility functions for the app."""

from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)


def get_keyword_suggestions(question: str) -> dict:
    """Initial prompt of the app. Ask the user what they want to research.

    Return dictionary with arxiv categories, keywords, similar questions and
    sorting criteria.
    """
    response_schemas = [
        ResponseSchema(
            name="categories",
            description="list arxiv categories that could be useful for the user. Use"
            " the arxiv category names (e.g. 'astro-ph.GA')",
        ),
        ResponseSchema(
            name="similar questions",
            description="list questions that could also be of interest for the user.",
        ),
        ResponseSchema(
            name="keywords",
            description="List relevant keywords for the user research. "
            "Be specific. Avoid keywords that are too general (e.g. 'theory', "
            "'recent', 'paper', 'study', 'science') "
            "Feel free to add keywords that the are not mentioned in by the user.",
        ),
        ResponseSchema(
            name="sort by",
            description="which sorting criteria could more useful for the user"
            " (relevance or submission date).",
        ),
    ]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()

    prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(
                "Help the user with their research as best as possible. "
                "\n{format_instructions}"
            ),
            HumanMessagePromptTemplate.from_template("{question}"),
        ],
        input_variables=["question"],
        partial_variables={"format_instructions": format_instructions},
    )

    _input = prompt.format_prompt(question=question)

    chat = ChatOpenAI(model="gpt-3.5-turbo")
    output = chat(_input.to_messages())
    return output_parser.parse(output.content)
