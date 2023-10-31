# Research Collections 📖

A Streamlit web app, that leverages the capabilities of Large Language Models (LLMs)
to perform simple reasoning tasks. The app revolves around the concept of
**research collections** which are curated sets of paper metadata obtained from
ArXiv. Users can interact with these collections to explore the research landscape,
identify emerging trends, and receive personalized paper recommendations.

---

## Overview

Make the research process more efficient and enjoyable.
Uses LLMs agents to assist you in finding relevant literature.
The app is divided into four sections:

- **Keyword Generation**: Generate highly relevant keywords for your research.
This is a two-step process. First, an LLM is prompted to generate a
small list of relevant keywords, using its own internal parameters. This list is good,
but tends to be repetitive and usually lacks in-domain knowledge.
To refine the list, the app downloads from ArXiv a small sample of paper titles.
The titles are then fed to the LLM, which uses them to generate a new list of
refined keywords, witch now contain domain-specific knowledge.

<p align="center">
  <img src="img/keyword_agent.png" alt="keyword" width="400"/>
</p>

- **Research collections**: Download papers from ArXiv using the refined keywords.
The abstracts are vectorized with the **bge-small-en-v1.5** embedding model
and are stored in a **Milvus** vector database.

<p align="center">
  <img src="img/Store abstracts.png" alt="keyword" width="400"/>
</p>

- **Research landscape**: Use BERTopic to identify the underlying topics in your
research collection. Use the powerful visualizations to identify research topics,
outliers, and new trends in the field.

<p align="center">
  <img src="img/research landscape.png" alt="keyword" width="400"/>
  <img src="img/topic_over_time.png" alt="topic over time" width="400"/>
</p>

- **Paper Scoring**: Explore your research collections using Retrival Augmented
Generation. Ask questions in natural language and let an LLM identify which
papers are a **must-read**.

<p align="center">
  <img src="img/Paper recommendations.png" alt="paper recommendations" width="400"/>
</p>


---

## Getting Started

To use the streamlit app, you will need an [OpenAI developer account](https://platform.openai.com/) and an API key.
By default, research collections uses *gpt-3.5-turbo* as the default LLM model.

### Cloning the Repository

1. Install Poetry

[Poetry](https://python-poetry.org/docs/#installation) is a tool for dependency management and packaging in Python.
It uses the pyproject.toml file to manage dependencies and build the package.

2. **Install Milvus**

Milvus is an open-source vector database that provides state-of-the-art similarity
search.

Download Milvus from [here](https://milvus.io/docs/install_standalone-docker.md)
and follow the instructions to install it the latest version. It requires Docker
and Docker Compose.

3. **Clone this GitHub repository**

```
git clone https://github.com/lgarma/research-assistant.git
```

4. **Set up the virtual environment with poetry**

```bash
cd research-assistant
poetry install
poetry shell
```

4. **Set your OpenAI API key**

```bash
echo "OPENAI_API_KEY=your-api-key" > .env
```

5. **Initiate the streamlit app**

```bash
poetry run streamlit run app/01_📖_Research_collection.py
```

### Docker Installation
If you prefer to use Docker, you can set up Research Assistant as follows:

1. **Clone this GitHub repository**

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

4. **Open the streamlit app**

The streamlit app should be running on http://localhost:8502
