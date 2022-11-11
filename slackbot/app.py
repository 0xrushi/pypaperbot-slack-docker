import requests
from urllib.parse import urlparse
import os 
import slack
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
import subprocess
import glob
from threading import Thread
from slack.errors import SlackApiError
from time import sleep
import io 
import requests

QUEUE_API_INSERT_URL = "http://YOUR_QUEUE_API_URL:3000/api/task"

env_path = Path('.') /'.env'
load_dotenv(env_path)

app = Flask(__name__)

client = slack.WebClient(token=os.environ['SLACK_TOKEN_'])

if not os.path.exists("output"):
    os.makedirs("output")

def fetch_and_upload_file_in_background(channel_id, user_name, url):
    subprocess.call(f'PyPaperBot --doi="{url}" --dwn-dir="output/"', shell=True)
    sleep(15)
    try:
        generated_pdf = glob.glob("/root/output/*.pdf")
        print("generatsss si , ", generated_pdf)
        if len(generated_pdf) ==0:
            client.chat_postMessage(channel=channel_id, text="Something went wrong.... Your request is being forwarded to a high priority queue, this may take 24-48hrs 😛 \n You can track your queue at http://141.148.21.167:3000/")
            # add the url to todo list
            myobj = {'title': str(url)}
            x = requests.post(QUEUE_API_INSERT_URL, json = myobj)
            # add the username to todo list
            myobj = {'title': str(user_name)}
            x = requests.post(QUEUE_API_INSERT_URL, json = myobj)
            print(x.text)
        generated_pdf = generated_pdf[0]
        # Call the files.upload method using the WebClient
        result = client.files_upload(
            channels=channel_id,
            initial_comment="Here's your file :smile:",
            file=generated_pdf,
        )
        os.remove(generated_pdf)
        return Response(), 200
    except SlackApiError as e:
        client.chat_postMessage(channel=channel_id, text="Failed to get PDF")
        print(e)

@ app.route('/get_from_doi', methods=['POST'])
def get_from_doi():
    data = request.form
    user_name = data.get('user_name')
    channel_id = data.get('channel_id')
    url = data.get('text')

    thr = Thread(target=fetch_and_upload_file_in_background, args=[channel_id, user_name, url])
    thr.start()
    client.chat_postMessage(channel=channel_id, text="Processing your request")
    return Response(), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
