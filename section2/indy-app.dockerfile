FROM ubuntu:18.04

RUN useradd -ms /bin/bash indy

# Install environment
RUN apt-get update -y && apt-get install -y \
    wget \
    python3.7 \
    python3-pip \
    python-setuptools \
    apt-transport-https \
    ca-certificates \
    software-properties-common

WORKDIR /home/indy

RUN pip3 install --upgrade pip
RUN pip3 install -U \
    pip \
    setuptools \
    python3-indy==1.11.0 \
	fastapi \
	PyYAML==6.0 \
	httptools==0.3.0 \
	python-dotenv==0.20.0 \
	uvicorn==0.16.0 \
	uvloop==0.14.0 \
	watchgod==0.7 \
	websockets==9.1 \
	requests \
	black

RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88 \
    && add-apt-repository "deb https://repo.sovrin.org/sdk/deb xenial stable" \
    && apt-get update \
    && apt-get install -y \
    libindy=1.11.0

USER indy

EXPOSE 8888 5000
