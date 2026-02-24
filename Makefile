IMAGE_NAME = scraper-service
PORT = 5555

.PHONY: build run run-env stop
build:
	docker build -t $(IMAGE_NAME) .

run:
	docker run --rm -it -p $(PORT):$(PORT) --name $(IMAGE_NAME) $(IMAGE_NAME)

run-env:
	docker run --rm -it -p $(PORT):$(PORT) --env-file .env --name $(IMAGE_NAME) $(IMAGE_NAME)

stop:
	docker stop $(IMAGE_NAME)
