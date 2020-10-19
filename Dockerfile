#  Para atualizar uma imagem basta executar o comando 
FROM python:3.6

ENV PYTHONNUNBUFFERD 1

# Update aptitude with new repo
RUN apt update
RUN apt -y upgrade

RUN apt install -y python3-pip

RUN apt install -y build-essential libssl-dev libffi-dev python3-dev

RUN echo "/nuvols/" > /usr/local/lib/python3.6/site-packages/nuvols.pth
#RUN echo "/nuvols/" > usr/local/lib/python3.7/site-packages/nuvols.pth 
#RUN echo "/nuvols/core/" > usr/local/lib/python3.7/dist-packages/core.pth 

RUN mkdir /nuvols
WORKDIR /nuvols

COPY . /nuvols

RUN pip install -U pip

# Install requirements
RUN pip install -r core/requirements_dev.txt
