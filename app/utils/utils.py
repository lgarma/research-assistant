"""Utility functions for the app."""
import arxiv
from langchain.schema import Document


def get_arxiv_documents(
    query: str, sort_by: str = "relevance", max_results=5
) -> list[Document]:
    """Get arxiv documents using the query."""
    results = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
        if sort_by == "relevance"
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
            },
        )
        for result in results.results()
    ]
