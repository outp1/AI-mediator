FROM python:3.9-buster
ENV PROJECT_NAME=$PROJECT_NAME

WORKDIR /usr/src/app/"$PROJECT_NAME"


COPY requirements.txt /usr/src/app/"$PROJECT_NAME"
RUN pip install -r /usr/src/app/"$PROJECT_NAME"/requirements.txt
COPY . /usr/src/app/"$PROJECT_NAME"
