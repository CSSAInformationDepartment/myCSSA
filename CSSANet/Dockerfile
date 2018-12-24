
FROM python:3.6-slim

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Development Mode Secret Key
ENV DJANGOKEYDEV '=3qm1_ubi+$_bzvcj0yxoq+52q!l9+k*za&s06@z1#pee9bd2l' 
ENV DJANGOKEYPD 'PRODUCTIONTEST'

RUN apt-get update && apt-get install -y netcat

RUN mkdir /code
WORKDIR /code

RUN mkdir /config
RUN mkdir /data
ADD requirements.txt /code/
#ADD alice-bootloader.sh /code/
RUN chmod g+w /code/
RUN chmod g+w /data/

# Install dependencies
RUN pip3 install --upgrade pip

RUN pip3 install -r /code/requirements.txt







