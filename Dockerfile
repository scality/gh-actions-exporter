FROM python:3.11

EXPOSE 8000

ENV POETRY_VERSION=1.6.1

ENV PATH=$PATH:/root/.poetry/bin

RUN apt-get update && apt-get install curl -y

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-dev

COPY . /app/

CMD uvicorn gh_actions_exporter.main:app --host 0.0.0.0 --port 8000
