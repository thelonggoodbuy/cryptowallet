# pull official base python image
FROM python:3.11.9

# work directory inside docker image
WORKDIR /usr/src/app

#  set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install libraries
RUN apt update
RUN echo y|apt install postgresql
RUN apt install postgresql-contrib
RUN apt install libpq-dev
RUN pip install psycopg2
RUN apt install -y netcat-traditional
RUN apt install make
RUN echo y|apt install vim
RUN echo y|apt install libevent-dev

# instale locales
# RUN apt-get update && apt-get install -y locales
# RUN locale-gen uk_UA.UTF-8
# ENV LANG uk_UA.UTF-8
# ENV LANGUAGE uk_UA:uk
# ENV LC_ALL uk_UA.UTF-8

RUN apt-get update && \
    apt-get install -y locales && \
    sed -i -e 's/# uk_UA.UTF-8 UTF-8/uk_UA.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales



ENV LANG uk_UA.UTF-8
ENV LC_ALL uk_UA.UTF-8

# install dependencies
RUN pip install --upgrade pip
# RUN pip install gunicorn
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r /usr/src/app/requirements.txt

COPY ./entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh
RUN echo '-----------1---------------------------------------'

COPY . /usr/src/app/


ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
