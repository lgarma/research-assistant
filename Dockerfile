FROM python:3.10.13-bullseye

COPY . /root/app/
WORKDIR /root/app

RUN apt-get update

# Set PYTHONPATH
ENV PYTHONPATH=${PYTHONPATH}:${PWD}

# Manage SSH Keys to GitHub install
USER root

RUN pip install poetry

RUN poetry config installer.max-workers 10

RUN mkdir -p /root/app/logs && \
    poetry install --no-dev --no-interaction --no-ansi -vvv

EXPOSE 8602

HEALTHCHECK CMD curl --fail http://localhost:8602/_stcore/health

ENTRYPOINT ["poetry", "run", "streamlit", "run", "app/01_✨_Research_Assistant.py", "--server.port=8602", "--server.enableCORS=false", "--server.enableXsrfProtection=false", "--theme.base=dark"    , "--theme.primaryColor=#9333ea", "--theme.font=monospace", "--theme.textColor=#f1f5f9", "--server.fileWatcherType=none", "--browser.serverAddress=localhost"]
