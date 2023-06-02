import gradio as gr
import os
from pathlib import Path
import subprocess
import glob
import csv
from threading import Thread, Timer
from time import sleep, time, strftime
import datetime
import logging
import re
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

csv_file = f"{output_dir}/file_status.csv"


def fetch_and_upload_file(url, ignorethis):
    logging.info("fetch_and_upload_file called")
    command = f'PyPaperBot --doi="{url}" --dwn-dir="{output_dir}/"'
    # result = subprocess.call(command, shell=True)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    
    sleep(10)
    
    result = process.returncode
    
    command_output = stdout.decode().strip() if stdout else ""
    
    logging.info(f"output is {command_output}")
    
    save_name = re.search(r"Download \d+ of \d+ -> (.+)", command_output)
    
    if save_name:
        save_name = save_name.group(1)

    if result == 0 and save_name and save_name != "None":
        generated_pdf = f"{save_name}.pdf"
        save_to_csv(url, generated_pdf)
        return generated_pdf
    save_to_csv(url, None)
    return None

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

def delete_files():
    threshold = 10 * 60  # 10 minutes in seconds
    while True:
        for file_path in glob.glob(f"{output_dir}/*.pdf"):
            creation_time = os.path.getctime(file_path)
            elapsed_time = time() - creation_time
            if elapsed_time > threshold:
                os.remove(file_path)
        sleep(60)  # Check every 60 seconds

if __name__ == "__main__":
    t = Thread(target=delete_files)
    t.start()


    if os.stat(csv_file).st_size == 0:
        with open(csv_file, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["URL", "File Path", "Timestamp"])

    input_text = gr.inputs.Textbox(lines=2, label="Enter the DOI URL here")

    total_downloads_today, total_fail_downloads_today = calculate_total_downloads_today(csv_file)
    downloads_status = gr.Label(label="Current Status", value={"Total downloads today (ignore % sign)": total_downloads_today/100, "Total failed downloads today": total_fail_downloads_today/100})

    output_file = gr.outputs.File(label="Download Output")

    iface = gr.Interface(fn=fetch_and_upload_file, inputs=[input_text, downloads_status], outputs=output_file, examples=[["https://doi.org/10.1007/978-3-319-29799-6"]],)

    iface.launch(share=True, server_name="0.0.0.0", server_port=7861)