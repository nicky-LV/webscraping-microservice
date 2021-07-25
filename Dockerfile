FROM python:3.8-buster
COPY . /webscraping_app
WORKDIR /webscraping_app
RUN apt-get update -y && apt install sudo && sudo apt install wait-for-it
RUN pip install -r requirements.txt
RUN chmod 775 ./start_server.sh