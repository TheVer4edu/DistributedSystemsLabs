FROM python:3.8

WORKDIR /app

RUN pip install pipenv

COPY Pipfile.lock Pipfile.lock

RUN pipenv sync

COPY ./ /app

CMD pipenv run python main.py