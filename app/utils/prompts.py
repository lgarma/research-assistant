"""Prompts for the LLMs."""


def first_keywords_prompt(question: str) -> str:
    """Prompt for the first keyword generation."""
    return (
        "Keyword Generator: Tell me your research interest and I will provide a short"
        "list of relevant keywords. \n\n"
        "User: Today I want to research: Stellar evolution \n\n"
        "Keyword Generator: [Stellar evolution, Stellar lifecycles, "
        "Main sequence stars, Red giant phase, Supernova, White dwarf, "
        "Protostar formation, Nuclear fusion, Stellar nucleosynthesis, "
        "Hertzsprung-Russell diagram] \n\n"
        "User: I want to research: room temperature superconductors \n\n"
        "Keyword Generator: [Superconductivity, Room Temperature superconductors, "
        "Superconducting Materials, Superconducting Phase Transitions, Cooper Pairs, "
        "Critical Temperature, BCS Theory, Meissner Effect, Magnetic Levitation, "
        "Iron-based superconductors] \n\n"
        "User: Can you suggest some relevant keywords for my research: "
        f"{question}. \n\n"
        f"Keyword Generator: ["
    )


def refine_keywords_prompt(question: str, top_papers: list[str]) -> str:
    """Prompt for the keyword refinement."""
    return (
        f"I want to research: {question}. \n\n"
        "Here is a list of papers that could be useful: \n\n"
        f"Papers: {top_papers}. \n\n"
        "Give me a list of keywords that best describe the topics of these papers."
        "Separate the keywords with commas. Do not overextend. \n\n"
        "Sure, here is a relevant keyword list: ["
    )
