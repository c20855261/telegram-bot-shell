FROM python:3.9-slim-bullseye

MAINTAINER Ayo twops@twprotech.com

WORKDIR /app

ENV TZ=Asia/Shanghai
RUN set -ex \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && echo "LANG=en_US.utf8" > /etc/locale.conf \
    && echo "alias ll='ls -l'" >> ~/.bashrc

RUN apt-get update -y && \
    apt-get install -y vim openssh-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /tmp/*

COPY requirements.txt /app/

RUN pip install -r requirements.txt
#RUN pip install --no-cache-dir paramiko subprocess && \
#    pip install --no-cache-dir pyTelegramBotAPI==4.0.0

CMD ["tail", "-f", "/dev/null"]
