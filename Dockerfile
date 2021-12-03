FROM python:3.9

# TODO cleanup workdir setup
# set up code directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Install linux dependencies
RUN apt-get update && apt-get install -y libssl-dev

# install npm/ganache cli
RUN apt-get update && apt-get install -y \
    npm

RUN npm install -g ganache-cli

# install python libs
RUN pip install eth-brownie
RUN pip install flask
RUN pip install apscheduler

WORKDIR /projects

EXPOSE 5000

ENTRYPOINT [ "bash" ]
