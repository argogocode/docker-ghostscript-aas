FROM alpine:latest

#MAINTAINER 

# data should be mounted with a directory container your PDF's
RUN mkdir /data
VOLUME ["/data"]

RUN apk update
RUN apk add \
  pdftk \
  ghostscript \
  imagemagick \
  ghostscript-fonts \
  python-pip 

RUN pip install werkzeug executor gunicorn

#FROM openlabs/docker-wkhtmltopdf:latest
#MAINTAINER Sharoon Thomas <sharoon.thomas@openlabs.co.in>

# Install dependencies for running web service
#RUN apt-get install -y python-pip ghostscript
#RUN pip install werkzeug executor gunicorn

ADD app.py /app.py
EXPOSE 80

ENTRYPOINT ["usr/local/bin/gunicorn"]

# Show the extended help
CMD ["-b", "0.0.0.0:80", "--log-file", "-", "app:application"]
