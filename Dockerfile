# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

COPY Pipfile Pipfile.lock ./

RUN pip install pipenv
RUN pip install gunicorn 
RUN pipenv install --system --deploy

CMD [ "gunicorn", "api:app", "-w", "2", "--threads", "2", "-b", "0.0.0.0:6000"]