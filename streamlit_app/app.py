import streamlit as st
from celery import Celery
import time 
import os

simple_app = Celery('simple_worker',
                    broker='amqp://admin:mypass@rabbit.default.svc.cluster.local:5672',
                    backend='rpc://')

def main():
    st.title("RequestPaper revanced")
    examples = ["<select-an-example>", "https://doi.org/10.1007/978-3-319-29799-6"]
    selected_example = st.selectbox("Select an example", examples, index=0)

    url = st.empty()
    if selected_example == examples[1]:
        url = st.text_input("Enter text", value=examples[1], key = "url")
    else:
        # Get user input
        url = st.text_input("Enter the DOI URL here", key="url")

    # Trigger the Celery task
    if st.button("Fetch and Upload"):
        # result = fetch_and_upload_file.delay(url)
        result = simple_app.send_task('tasks.fetch_and_upload_file', kwargs={'url': url})
        task_id = result.id
        st.text(f"Task ID: {task_id}")

        # Placeholder for displaying task status
        status_text = st.empty()

        # Poll the task status
        while not result.ready():
            status_text.text("Task in progress...")
            status_text.text("Waiting for task completion...")
            status_text.text(f"Current task status: {result.status}")
            status_text.text(f"Current task result: {result.result}")
            time.sleep(2)

        # Task completed
        status_text.text("Task completed!")
        status_text.text(f"Task result: {result.result}")
        pdf_path, download_status = result.result
        if pdf_path:
            absolute_path = os.path.abspath(pdf_path)
        if pdf_path and download_status and os.path.exists(absolute_path):
            status_text.text("")
            
            file_name = pdf_path[7:]
            formatted_string = "<br>".join([f"{key}: {value}" for key, value in download_status.items()])

            st.markdown(f'**{file_name}** <br>{formatted_string}', unsafe_allow_html=True)

            file_bytes = open(absolute_path, "rb").read()
            st.download_button(label="Download PDF", data=file_bytes, file_name=file_name)
        else:
            st.markdown('**Sorry, couldn\'t find the url**', unsafe_allow_html=True)
            


if __name__ == "__main__":
    main()