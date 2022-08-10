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

env_path = Path('.') /'.env'
load_dotenv(env_path)

app = Flask(__name__)

client = slack.WebClient(token=os.environ['SLACK_TOKEN_'])

if not os.path.exists("output"):
    os.makedirs("output")

def upload_file_in_background(channel_id, generated_pdf):
    try:
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

@ app.route('/get_from_doi', methods=['POST'])
def get_from_doi():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    url = data.get('text')

    subprocess.call(f'PyPaperBot --doi="{url}" --dwn-dir="output/"', shell=True)
    generated_pdf = glob.glob("output/*.pdf")[0]

    thr = Thread(target=upload_file_in_background, args=[channel_id, generated_pdf])
    thr.start()
    client.chat_postMessage(channel=channel_id, text="Processing your request")
    return Response(), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
