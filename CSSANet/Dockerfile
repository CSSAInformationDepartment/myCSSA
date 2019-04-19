
FROM python:3.7.2-alpine3.8

# Set environment varibles

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Development Mode Secret Key
ENV DJANGOKEYDEV '=3qm1_ubi+$_bzvcj0yxoq+52q!l9+k*za&s06@z1#pee9bd2l' 
ENV DJANGOKEYPD '=3qm1_ubi+$_bzvcj0yxoq+52q!l9+k*za&s06@z1#PRODUCTION'

RUN apk add --update netcat-openbsd
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN apk add jpeg-dev zlib-dev
RUN rm -rf /var/cache/apk/*


RUN mkdir /code
RUN mkdir /config
RUN chmod g+w /code

WORKDIR /code
COPY code/* /code/

# Install dependencies
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

ENTRYPOINT ["sh", "alice-bootloader.sh" ]





