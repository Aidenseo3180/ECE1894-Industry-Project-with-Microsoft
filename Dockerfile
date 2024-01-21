ARG PYTHON_VERSION=3.10

# getting base image
FROM python:${PYTHON_VERSION}-alpine

ARG POETRY_VERSION=1.7.1

# install system dependencies
# you need libffi-dev because some dependencies from poetry requires C compiler to download
RUN apk add gcc musl-dev libffi-dev \
	&& pip install "poetry==${POETRY_VERSION}"

# copy only requirements to cache them in docker layer
WORKDIR /code
COPY poetry.lock pyproject.toml /code/

# project initialization
RUN poetry install --no-dev \
    && poetry config virtualenvs.create false

# copy the current directory contents into the container at /code
COPY . /code

# run to test if container runs
CMD [ "echo", "Hello World" ]