# Research Assistant 🧠

**Use a LLM assistants to become familiar with the research landscape.
Create a knowledge database, explore topics, identify relevant papers, and new trends.**


---

## 📖 Overview

Research Assistant uses different LLMs agents to assist researchers in various
aspects of their work.

- **Keyword Generation**: Generate highly relevant keywords for your research topic.
This agent, works in two steps. First, an LLM assistant is prompted to generates a
small list of relevant keywords, using its own internal parameters. Usually, this
first list is good, but not very specific and lacks domain-specific terms.
To refine the list, a small sample of titles from arxiv is fed back to the agent,
which uses them to generate a new list of keywords that is more tailored to your research.
- **Knowledge database**: Download papers from arxiv using the refined list of keywords.
The abstracts are vectorized using **bge-small-en-v1.5** and saved in a **Milvus**
vector database.
- **Topic Identification**: Use BERTopic to identify the main topics in the knowledge database.
Get a description in natural language of each topic and the get some representative papers.
Use the topic model to identify research topics, outliers, and recent trends.
- **Paper Scoring**: Explore the knowledge database using Retrival Augmented Generation (RAG).
Ask questions and identify which papers are a **must-read**.

---

## Getting Started

Make sure you have one of the following installed:

- Poetry
- Docker and Docker Compose

Also, you will need an OpenAI developer account and an API key. You can get one
[here](https://platform.openai.com/).

### Cloning the Repository

1. **Clone the GitHub repository**

```
git clone https://github.com/lgarma/research-assistant.git
```

2. **Set up the virtual environment**

```bash
cd research-assistant
poetry install
```

3. **Set your OpenAI API key**

```bash
echo "OPENAI_API_KEY=your-api-key" > .env
```

4. **Initiate the webapp**

```bash
poetry run streamlit run app/01_🧠_Knowledge_collection.py
```

### Docker Installation
If you prefer to use Docker, you can set up Research Assistant as follows:

1. **Clone the GitHub repository**

```bash
git clone https://github.com/lgarma/research-assistant.git
```

2. **Set your OpenAI API key**

```bash
echo "OPENAI_API_KEY=your-api-key" > .env
```

3. **Build and run the docker container**

```bash
docker-compose up --build -d
```
