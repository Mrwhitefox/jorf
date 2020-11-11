FROM python:3.7-slim

RUN apt-get update && apt-get install -y locales && apt-get clean
RUN echo "fr_FR.UTF-8 UTF-8" >> /etc/locale.gen && locale-gen 
ADD jorf_http.py main.py requirements.txt /opt/jorf/

ADD parsers /opt/jorf/parsers
ADD queries /opt/jorf/queries
ADD views /opt/jorf/views
ADD utils /opt/jorf/utils
ADD config/docker.yml /opt/jorf/config/docker.yml

RUN pip install -r /opt/jorf/requirements.txt

WORKDIR /opt/jorf/
EXPOSE 80/tcp
CMD [ "python", "/opt/jorf/jorf_http.py", "/opt/jorf/config/docker.yml" ]
