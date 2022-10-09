FROM python:3.8

WORKDIR /web

RUN pip install pipenv

COPY Pipfile.lock Pipfile.lock

RUN pipenv sync

EXPOSE 8000

COPY web /web

CMD ./run.sh