FROM python:3.7-slim

RUN apt update -y \
    && apt install -y default-libmysqlclient-dev \
    && apt install -y --no-install-recommends gcc

WORKDIR /requirements

COPY ./requirements.txt ./
RUN pip install -U pip && pip install -r requirements.txt

COPY ./dev_requirements.txt ./
RUN pip install -r dev_requirements.txt

WORKDIR /pocketbook

ENTRYPOINT ["bash", "./entrypoint.sh"]
