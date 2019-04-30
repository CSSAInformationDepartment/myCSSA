
FROM python:3.7.2-alpine3.8
EXPOSE 8000
# Set environment varibles

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/usr/local/lib/python3.7/site-packages/:/code/


# System dependency installation
## Network
RUN apk add --update netcat-openbsd

## Timezone
RUN apk add tzdata
RUN cp /usr/share/zoneinfo/Australia/Melbourne /etc/localtime
RUN echo "Australia/Melbourne" >  /etc/timezone
RUN date
RUN apk del tzdata


## Python Runtime
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN apk add jpeg-dev zlib-dev
RUN rm -rf /var/cache/apk/*


RUN mkdir /code
RUN chmod g+w /code

WORKDIR /code
COPY code/ /code/
RUN chmod g+w /code/static
RUN chmod g+w /code/media
RUN ls -la /code/*


# Install dependencies
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

ENTRYPOINT ["sh", "alice-bootloader.sh" ]





