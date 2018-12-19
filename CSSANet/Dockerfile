
FROM python:3.6-slim

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Development Mode Secret Key
ENV DJANGOKEYDEV '=3qm1_ubi+$_bzvcj0yxoq+52q!l9+k*za&s06@z1#pee9bd2l' 
ENV DJANGOKEYPD '' 

RUN mkdir /code
WORKDIR /code
# Copy project
COPY . /code/

RUN mkdir /config

# Install dependencies
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Make app folder writable for the sake of db.sqlite3, and make that file also writable.
RUN chmod g+w /code/

RUN python3 /code/manage.py collectstatic  --noinput





