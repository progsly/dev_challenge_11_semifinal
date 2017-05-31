FROM python:2.7

EXPOSE 8000

RUN apt-get update && apt-get install -y mysql-client python-bs4 libmysqlclient-dev python-dev

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install -r requirements.txt

COPY . /usr/src/app

CMD python main.py