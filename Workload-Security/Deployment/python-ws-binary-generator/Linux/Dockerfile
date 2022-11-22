FROM python:latest

RUN apt update -y && apt install -y tar wget gcc make

WORKDIR /root

RUN wget https://github.com/neurobin/shc/archive/release.tar.gz && tar -xvf release.tar.gz && cd shc-release && ./configure && make && make install && cd .. && rm -rf shc-release release.tar.gz

ADD ../app.py /root/app.py

ENV REGION=REGION APIKEY=APIKEY PLATFORM=PLATFORM

RUN app.py --c1region $REGION --apikey $APIKEY

RUN shc -f ws.sh && rm ws.sh && mv ws.sh.x /root/CloudOne