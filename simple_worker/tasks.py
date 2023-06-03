import time
from celery import Celery
from celery.utils.log import get_task_logger
import subprocess
import os
import logging
import re
import csv
import datetime
from time import sleep, time, strftime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logger = get_task_logger(__name__)
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)
csv_file = f"{output_dir}/file_status.csv"

def save_to_csv(url, file_path):
    timestamp = strftime("%Y-%m-%d %H:%M:%S")
    with open(csv_file, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([url, file_path, timestamp])

def calculate_total_downloads_today(csv_file):
    if not os.path.isfile(csv_file):
        return 0, 0
    
    current_date = datetime.date.today()
    total_downloads = 0
    total_failed_downloads = 0
    
    with open(csv_file, mode="r") as file:
        reader = csv.reader(file)
        header = next(reader)  # Skip the header row
        for row in reader:
            timestamp = datetime.datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")
            if timestamp.date() == current_date:
                total_downloads += 1
                if row[1] == "None" or row[1] == "None.pdf":
                    total_failed_downloads += 1
    
    return total_downloads, total_failed_downloads

app = Celery('tasks',
             broker='amqp://admin:mypass@rabbit:5672',
             backend='rpc://')


@app.task()
def longtime_add(x, y):
    logger.info('Got Request - Starting work ')
    time.sleep(4)
    logger.info('Work Finished ')
    return x + y

@app.task()
def fetch_and_upload_file(url, ignorethis=None):
    logging.info("fetch_and_upload_file called, url received " + url)
    command = f'PyPaperBot --doi="{url}" --dwn-dir="{output_dir}/"'
    # result = subprocess.call(command, shell=True)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=os.getcwd())
    stdout, stderr = process.communicate()

    sleep(10)

    result = process.returncode

    command_output = stdout.decode().strip() if stdout else ""

    logging.info(f"output is {command_output}")

    save_name = re.search(r"Download \d+ of \d+ -> (.+)", command_output)

    if save_name:
        save_name = save_name.group(1)

    if result == 0 and save_name and save_name != "None" and save_name != "":
        generated_pdf = f"{output_dir}/{save_name}.pdf"
        save_to_csv(url, generated_pdf)

        total_downloads_today, total_fail_downloads_today = calculate_total_downloads_today(csv_file)
        # download status
        ds = {"Total downloads today": total_downloads_today, "Total failed downloads today": total_fail_downloads_today}
        return generated_pdf, ds

    save_to_csv(url, None)
    return None, None

