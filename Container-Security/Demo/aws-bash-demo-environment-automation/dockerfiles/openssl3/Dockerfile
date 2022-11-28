FROM ubuntu:jammy-20221020

RUN apt-get update              && \
    apt-get install nodejs  -y  && \
    rm -rf /var/lib/apt/lists/* 

COPY app/app.js /tmp/app.js

EXPOSE 80

ENTRYPOINT [ "node", "tmp/app.js" ]