.PHONY: build run clean

IMAGE_NAME := gradio-app
CONTAINER_NAME := gradio-container
PORT := 7861

build:
	docker build -t $(IMAGE_NAME) .

run:
	docker run  --name $(CONTAINER_NAME) -p $(PORT):$(PORT) $(IMAGE_NAME)

clean:
	docker stop $(CONTAINER_NAME)
	docker rm $(CONTAINER_NAME)
	docker rmi $(IMAGE_NAME)
