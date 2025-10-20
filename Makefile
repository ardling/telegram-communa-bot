PROJECT = lobby-bot
CHART_PATH = ./charts/$(PROJECT)/
SUBREPO = library
REPOSITORY = harbor.kube.local/$(SUBREPO)
DOCKER_IMAGE = $(REPOSITORY)/$(PROJECT)
REPO_FULL = $(REPOSITORY)/$(PROJECT)

.PHONY: check
check:
	helm lint $(CHART_PATH)
	helm template $(CHART_PATH)

.PHONY: build
build: check
	# docker tag SOURCE_IMAGE[:TAG] harbor.kube.local/library/REPOSITORY[:TAG]
	docker build -t $(DOCKER_IMAGE):latest .
	helm package $(CHART_PATH) -d ./dist/

.PHONY: push
push: build
	docker push $(DOCKER_IMAGE):latest
	helm push ./dist/$(PROJECT)-*.tgz oci://$(REPOSITORY)

.PHONY: dev
dev:
	$(shell helm upgrade lobby ./charts/lobby-bot -n dev --set telegram_token="$TELEGRAM_BOT_TOKEN" --set bot_admin="$BOT_ADMIN")
