PROJECT = lobby-bot
CHART_PATH = ./charts/$(PROJECT)/
SUBREPO = library
REPOSITORY = harbor.kube.local/$(SUBREPO)
DOCKER_IMAGE = $(REPOSITORY)/$(PROJECT)
REPO_FULL = $(REPOSITORY)/$(PROJECT)
TEST_PARAMS = --set telegram_token="TG_TOKEN" --set bot_admin="admin_user"
NAMESPACE = dev

.PHONY: check
check:
	helm lint $(CHART_PATH) $(TEST_PARAMS)
	helm template $(CHART_PATH) $(TEST_PARAMS)

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
	helm upgrade lobby ./charts/lobby-bot -n $(NAMESPACE) --set telegram_token="${TELEGRAM_BOT_TOKEN}" --set bot_admin="${BOT_ADMIN}" --set image.pullPolicy=Always
	kubectl rollout restart deployment/lobby-lobby-bot -n $(NAMESPACE)
