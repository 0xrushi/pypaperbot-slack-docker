FROM python:3.10-alpine
WORKDIR /root
RUN apk update
RUN apk add make gcc automake g++ subversion python3-dev
RUN pip install --upgrade pip
RUN pip install PyPaperbot slackclient python-dotenv flask
EXPOSE 5000
CMD python app.py