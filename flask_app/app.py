import streamlit as st
from celery import Celery
import time 
import os

simple_app = Celery('simple_worker',
                    broker='amqp://admin:mypass@rabbit:5672',
                    backend='rpc://')


# @app.route('/simple_start_task')
# def call_method():
#     app.logger.info("Invoking Method ")
#     r = simple_app.send_task('tasks.fetch_and_upload_file', kwargs={'x': 1, 'y': 2})
#     app.logger.info(r.backend)
#     return r.id


# @app.route('/simple_task_status/<task_id>')
# def get_status(task_id):
#     status = simple_app.AsyncResult(task_id, app=simple_app)
#     print("Invoking Method ")
#     return "Status of the Task " + str(status.state)


# @app.route('/simple_task_result/<task_id>')
# def task_result(task_id):
#     result = simple_app.AsyncResult(task_id).result
#     return "Result of the Task " + str(result)


def main():
    st.title("Celery Streamlit App")

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
        absolute_path = os.path.abspath(pdf_path)
        status_text.text("")
        
        file_name = pdf_path[7:]
        formatted_string = "<br>".join([f"{key}: {value}" for key, value in download_status.items()])

        st.markdown(f'**{file_name}** <br>{formatted_string}', unsafe_allow_html=True)

        file_bytes = open(absolute_path, "rb").read()
        st.download_button(label="Download PDF", data=file_bytes, file_name=file_name)


if __name__ == "__main__":
    main()