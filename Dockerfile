ARG PYTHON_VERSION=3.12

# getting base image
FROM python:${PYTHON_VERSION}-alpine

# keep docker image running
ENTRYPOINT ["tail", "-f", "/dev/null"]

# install system dependencies
RUN pip install pytest \ 
&& pip install pytest-xdist \
&& pip install kubernetes

# copy only requirements to cache them in docker layer
WORKDIR /code

# copy the current directory contents into the container at /code
COPY . /code
