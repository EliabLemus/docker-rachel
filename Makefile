# When in doubt `make help`

## Overridable values
REGISTRY?=registry.gitlab.com
IMAGE_NAME?=rachel
TAGS?=latest 0.1.1

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

.PHONY: publish
publish: ## Pushes all images into the configured registry
	$(foreach tag,$(TAGS),\
		docker image push $(IMAGE_FULL_NAME):$(tag); )

.PHONY: build_armv6
build_armv6:
	docker image build -f arm/Dockerfile --platform linux/arm/v6 -t $(IMAGE_FULL_NAME)-armv6:$(DEFAULT_TAG) .
	$(foreach tag,$(subst $(DEFAULT_TAG),,$(TAGS)),\
		docker image tag $(IMAGE_FULL_NAME)-armv6:$(DEFAULT_TAG) $(IMAGE_FULL_NAME)-armv6:$(tag); )

.PHONY: publish_armv6
publish_armv6:
	$(foreach tag,$(TAGS),\
		docker image push $(IMAGE_FULL_NAME)-armv6:$(tag); )

.PHONY: build_armv7
build_armv7:
	docker image build -f arm/Dockerfile --platform linux/arm/v7 -t $(IMAGE_FULL_NAME)-armv7:$(DEFAULT_TAG) .
	$(foreach tag,$(subst $(DEFAULT_TAG),,$(TAGS)),\
		docker image tag $(IMAGE_FULL_NAME)-armv7:$(DEFAULT_TAG) $(IMAGE_FULL_NAME)-armv7:$(tag); )

.PHONY: publish_armv7
publish_armv7:
	$(foreach tag,$(TAGS),\
		docker image push $(IMAGE_FULL_NAME)-armv7:$(tag); )

.PHONY: build_armv8
build_armv8:
	docker image build -f arm/Dockerfile --platform linux/arm/v8 -t $(IMAGE_FULL_NAME)-armv8:$(DEFAULT_TAG) .
	$(foreach tag,$(subst $(DEFAULT_TAG),,$(TAGS)),\
		docker image tag $(IMAGE_FULL_NAME)-armv8:$(DEFAULT_TAG) $(IMAGE_FULL_NAME)-armv8:$(tag); )

.PHONY: publish_armv8
publish_armv8:
	$(foreach tag,$(TAGS),\
		docker image push $(IMAGE_FULL_NAME)-armv8:$(tag); )


.PHONY: clean
clean: ## Cleans docker env
	docker image rm -f $(foreach tag,$(TAGS), $(IMAGE_FULL_NAME):$(tag))
	docker image rm -f $(foreach tag,$(TAGS), $(IMAGE_FULL_NAME)-armv6:$(tag))
	docker image rm -f $(foreach tag,$(TAGS), $(IMAGE_FULL_NAME)-armv7:$(tag))
	docker image rm -f $(foreach tag,$(TAGS), $(IMAGE_FULL_NAME)-armv8:$(tag))
	docker system prune -f

.PHONY: help
help: ## Prints out this Makefile usage
	-@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
