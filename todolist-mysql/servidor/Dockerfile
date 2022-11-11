FROM python:3.6

EXPOSE 5002

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY todo.py /app
CMD python todo.py
