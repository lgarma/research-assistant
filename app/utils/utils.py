"""Utility functions for the app."""
import arxiv
from langchain.schema import Document


def get_arxiv_documents(
    query: str, sort_by: str = "Relevance", max_results=5
) -> list[Document]:
    """Get arxiv documents using the query."""
    results = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
        if sort_by == "Relevance"
        else arxiv.SortCriterion.SubmittedDate,
    )

    return [
        Document(
            page_content=result.summary,
            metadata={
                "Published": result.published.year,
                "Title": result.title,
                "Authors": result.authors,
                "Link": result.entry_id,
                "Comment": result.comment,
                "Journal Reference": result.journal_ref,
            },
        )
        for result in results.results()
    ]
