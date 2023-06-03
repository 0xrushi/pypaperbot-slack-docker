FROM python:3.8-slim

# layer caching for faster builds
COPY requirements.txt /
RUN pip install -r /requirements.txt

#COPY app.py /app.py
ADD . /streamlit_app
WORKDIR /streamlit_app

ENV FLASK_ENV=development

CMD streamlit run --server.address 0.0.0.0 app.py

EXPOSE 8501

#CMD gunicorn --workers $WORKERS \
#  --threads $THREADS \
#  --bind 0.0.0.0:$PORT_APP \
#  --log-level DEBUG \
#  app:app