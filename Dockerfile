FROM ubuntu:latest
RUN apt-get update
RUN apt-get install -y software-properties-common vim
RUN add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get update
RUN apt-get install -y build-essential python3.6 python3.6-dev python3-pip python3.6-venv
RUN apt-get install -y git
RUN python3.6 -m pip install pip --upgrade
RUN python3.6 -m pip install wheel

RUN apt-get install -y net-tools inetutils-ping vpnc
COPY ./requirements.txt /logproxy/requirements.txt
WORKDIR /logproxy
RUN pip install  --no-cache-dir -r /logproxy/requirements.txt
EXPOSE 8080
EXPOSE 514
COPY . /logproxy
ENTRYPOINT ["/bin/bash"]
CMD ["init.sh"]