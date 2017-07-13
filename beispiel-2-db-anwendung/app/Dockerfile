FROM frolvlad/alpine-python3:latest

WORKDIR /app

RUN apk add --no-cache \
	py3-psycopg2

ADD server.py .
EXPOSE 5000
CMD ["python3", "server.py"]

