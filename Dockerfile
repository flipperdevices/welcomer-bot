FROM python:3.11-alpine

COPY /pyproject.toml /poetry.lock ./

RUN apk add --no-cache curl gcc libffi-dev musl-dev

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root

COPY . .

ENTRYPOINT ["python", "main.py"]
