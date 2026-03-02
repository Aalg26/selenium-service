IMAGE_NAME = scraper-service
PORT = 5555

PROJECT_ID ?= ""
SERVICE_ACCOUNT ?= ""

.PHONY: build run run-env stop deploy
build:
	docker build -t $(IMAGE_NAME) .

run:
	docker run --rm -it -p $(PORT):$(PORT) --name $(IMAGE_NAME) $(IMAGE_NAME)

run-env:
	docker run --rm -it -p $(PORT):$(PORT) --env-file .env --name $(IMAGE_NAME) $(IMAGE_NAME)

stop:
	docker stop $(IMAGE_NAME)

deploy:
	@if [ -z "$(PROJECT_ID)" ] || [ -z "$(SERVICE_ACCOUNT)" ]; then \
		echo "Error: Las variables PROJECT_ID o SERVICE_ACCOUNT están vacías."; \
		exit 1; \
	fi
	@echo "🔧 Seteando el proyecto activo en gcloud..."
	gcloud config set project $(PROJECT_ID)
	@echo "🚀 Desplegando en $(PROJECT_ID)..."
	gcloud builds submit --config cloudbuild.yaml --project $(PROJECT_ID) --substitutions=_SERVICE_ACCOUNT=$(SERVICE_ACCOUNT) .