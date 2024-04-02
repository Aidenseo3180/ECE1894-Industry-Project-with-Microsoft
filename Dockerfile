ARG PYTHON_VERSION=3.12

# getting base image
FROM python:${PYTHON_VERSION}-alpine

# keep docker image running
ENTRYPOINT ["tail", "-f", "/dev/null"]

ARG POETRY_VERSION=1.7.1

# install system dependencies
# you need libffi-dev because some dependencies from poetry requires C compiler to download
RUN apk add gcc musl-dev libffi-dev \ 
&& pip install "poetry==${POETRY_VERSION}"

# copy only requirements to cache them in docker layer
# pod_socketserver.py to instantiate gateway through sockets
WORKDIR /code
COPY poetry.lock pyproject.toml /src/ms_socketserver.py /code/

# project initialization
RUN poetry config virtualenvs.create false \
&& poetry install --no-interaction