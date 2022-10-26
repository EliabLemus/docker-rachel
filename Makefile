# When in doubt `make help`

## Overridable values
REGISTRY?=registry.gitlab.com
IMAGE_NAME?=imagenrachelbeta/docker-rachel
TAGS?=latest 0.1.0

## Computed values
IMAGE_FULL_NAME:=$(REGISTRY)/$(IMAGE_NAME)
DEFAULT_TAG:=$(firstword $(TAGS))

## Default goal
.PHONY: all
all: clean build

.PHONY: build
build: ## Builds Ranchel image then re-tag them
	docker image build -t $(IMAGE_FULL_NAME):$(DEFAULT_TAG) .
	$(foreach tag,$(subst $(DEFAULT_TAG),,$(TAGS)),\
		docker image tag $(IMAGE_FULL_NAME):$(DEFAULT_TAG) $(IMAGE_FULL_NAME):$(tag); )
	docker image build --platform linux/arm64 -t $(IMAGE_FULL_NAME)-arm:$(DEFAULT_TAG) .
	$(foreach tag,$(subst $(DEFAULT_TAG),,$(TAGS)),\
		docker image tag $(IMAGE_FULL_NAME):$(DEFAULT_TAG) $(IMAGE_FULL_NAME)-arm:$(tag); )

.PHONY: publish
publish: ## Pushes all images into the configured registry
	$(foreach tag,$(TAGS),\
		docker image push $(IMAGE_FULL_NAME):$(tag); )
	$(foreach tag,$(TAGS),\
		docker image push $(IMAGE_FULL_NAME)-arm:$(tag); )

.PHONY: clean
clean: ## Cleans docker env
	docker image rm -f $(foreach tag,$(TAGS), $(IMAGE_FULL_NAME):$(tag))
	docker image rm -f $(foreach tag,$(TAGS), $(IMAGE_FULL_NAME)-arm:$(tag))
	docker system prune -f

.PHONY: help
help: ## Prints out this Makefile usage
	-@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
