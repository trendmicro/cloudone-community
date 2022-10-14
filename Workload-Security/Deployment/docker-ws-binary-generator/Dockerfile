FROM ubuntu:latest

RUN apt update -y && apt install -y tar wget gcc make

WORKDIR /root

RUN wget https://github.com/neurobin/shc/archive/release.tar.gz && tar -xvf release.tar.gz && cd shc-release && ./configure && make && make install && cd .. && rm -rf shc-release release.tar.gz

ADD ws.sh /root/ws.sh

ENV TENANTID=TENANTID TOKEN=TOKEN

RUN shc -f ws.sh && rm ws.sh && mv ws.sh.x /root/CloudOne