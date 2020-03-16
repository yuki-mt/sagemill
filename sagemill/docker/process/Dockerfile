FROM python:3.7

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends jq

RUN mkdir /usr/src/app
WORKDIR /usr/src/app

COPY ./requirements.txt ./
RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
