"""Utility functions for the app."""
import os

from app.utils.prompts import first_keywords_prompt, refine_keywords_prompt
from app.utils.utils import get_arxiv_abstracts
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.output_parsers.pydantic import PydanticOutputParser
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.prompts.chat import BaseMessage
from pydantic import BaseModel, Field

instruct = OpenAI(
    model="gpt-3.5-turbo-instruct",
    temperature=0.01,
    openai_api_key=os.environ["OPENAI_API_KEY"],
)

chat = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.01,
    openai_api_key=os.environ["OPENAI_API_KEY"],
)


class KeywordsAgent:
    """Agent that generates relevant keywords.

    The agent uses gpt-3.5-turbo-instruct to generate a list of keywords that
    could be useful for the user research.
    These first keyword suggestions usually are not very specific and usually
    lack domain knowledge.
    To refine the suggestions the agent downloads a small sample of papers
    from arxiv using the provided keywords.
    The titles of these papers are fed back to the llm, this time with instructions
    to refine the keywords list.
    The agent returns a list of both the first keyword suggestions
    and the refined keywords.

    Parameters:
        question (str):
            The question that the user wants to research.

        n_exploratory_papers (int):
            The number of papers to download from arxiv to refine the keywords.

        sort_by (str):
            The sorting criteria for the arxiv papers.
    """

    def __init__(
        self, question: str, n_exploratory_papers: int = 30, sort_by="Relevance"
    ):
        """Initialize the agent."""
        self.question = question
        self.n_exploratory_papers = n_exploratory_papers
        self.sort_by = sort_by

    def _first_keyword_suggestion(self) -> str:
        """Get the first keyword suggestion from instruct gpt."""
        prompt = first_keywords_prompt(self.question)
        return instruct(prompt)[:-1]

    def _refine_keywords(self, papers: list[str]) -> str:
        """Ask gpt instruct to refine the keywords using the papers titles."""
        prompt = refine_keywords_prompt(self.question, papers)
        return instruct(prompt)[:-1]

    def __call__(self) -> tuple[list[str], list[str]]:
        """Get keyword suggestions from instruct"""
        first_keywords = self._first_keyword_suggestion()

        top_papers = get_arxiv_abstracts(
            query=first_keywords,
            max_results=self.n_exploratory_papers,
            sort_by=self.sort_by,
        )
        titles = [paper.metadata["title"] for paper in top_papers]

        refined_keywords = self._refine_keywords(papers=titles)
        return first_keywords.split(", "), refined_keywords.split(", ")


class ScorePapersAgent:
    """Label tha papers using chat llm.

    The agent uses gpt-3.5-turbo to score the relevance of the papers.
    The output should is a list of pydantic objects with the following schema:
    title, topics, score and reasoning for the score.
    """

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
            "use a separate the markdown snippets using a divider '---' "
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

        output = chat(_input.to_messages())
        return self.parse_output(output)

    def parse_output(self, output: BaseMessage) -> list[dict]:
        """Use output parser to parse the output"""
        pydantic_parser = self.get_parser()
        split = output.content.split("---")
        return [pydantic_parser.parse(s) for s in split]
