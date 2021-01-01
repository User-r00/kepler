FROM ubuntu

COPY . /app

WORKDIR /app

RUN apt-get update

RUN apt-get install -y python3-pip

RUN apt-get install -y python3

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "bot.py"]
