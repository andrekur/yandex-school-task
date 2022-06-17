FROM python:3.9.6

RUN pip install --upgrade pip

COPY . /app

COPY _CI/entrypoint.sh /app

WORKDIR /app

RUN chmod +x entrypoint.sh

RUN pip install -r _CI/requirements.txt