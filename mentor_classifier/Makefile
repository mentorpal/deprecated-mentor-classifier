DOCKER_IMAGE?=mentor-classifier
ROOT=$(shell dirname ${PWD})
VENV=.venv
$(VENV):
	$(MAKE) install

.PHONY: install
install: poetry-ensure-installed
	poetry config --local virtualenvs.in-project true
	poetry env use python3.8
	poetry install

.PHONY: poetry-build-classifier
poetry-build-classifier: $(VENV)
	poetry build

.PHONY: poetry-ensure-installed
poetry-ensure-installed:
	sh $(ROOT)/tools/poetry_ensure_installed.sh

.PHONY clean:
clean:
	rm -rf .venv htmlcov .coverage

.PHONY: deps-show
deps-show-outdated:
	poetry show --outdated

.PHONY: deps-update
deps-update:
	poetry update

.PHONY docker-build:
docker-build:
	docker build --no-cache -t $(DOCKER_IMAGE) .

.PHONY docker-run-shell:
docker-run-shell:
	docker run -it --rm  --entrypoint /bin/bash $(DOCKER_IMAGE)

# use to test dockerized training locally
.PHONY: docker-train
docker-train-%:
	docker run \
		-it \
		--rm \
		-v $(PWD)/tests/fixtures/data/$*:/data \
		-v $(PWD)/tests/fixtures/shared:/shared \
		-v $(PWD)/tests/fixtures/models/$*:/output \
	$(DOCKER_IMAGE) train --data /data/ --shared /shared --output /output 

.PHONY: docker-train-default
docker-train-default:
	docker run \
		-it \
		--rm \
		-v $(PWD)/tests/fixtures/data/:/data \
		-v $(PWD)/tests/fixtures/shared:/shared \
		-v $(PWD)/tests/fixtures/models/default:/output \
	$(DOCKER_IMAGE) traindefault --data /data/ --shared /shared --output /output 

.PHONY: format
format: $(VENV)
	cd $(ROOT) && $(MAKE) format

.PHONY: license
license:
	cd $(ROOT) && make license

PHONY: test
test: $(VENV)
	rm -rf tests/fixtures/data_out/*/*
	cd $(ROOT)/shared && $(MAKE) installed/word2vec.bin
	cd $(ROOT)/shared && $(MAKE) installed/sentence-transformer
	cd $(ROOT)/shared && $(MAKE) installed/spacy-model
	cd $(ROOT)/shared/ && $(MAKE) installed/pop_culture.csv
	poetry run coverage run \
		--omit="$(PWD)/tests $(VENV)" \
		-m py.test -vv $(args)

.PHONY: test-all
test-all: test-format test-lint test-types test-license test

.PHONY: test-format
test-format: $(VENV)
	cd $(ROOT) && $(MAKE) test-format

.PHONY: test-license
test-license: $(LICENSE) $(LICENSE_HEADER) $(VENV)
	cd $(ROOT) && $(MAKE) test-license

.PHONY: test-lint
test-lint: $(VENV)
	cd $(ROOT) && $(MAKE) test-lint

.PHONY: test-types
test-types: $(VENV)
	cd $(ROOT) && $(MAKE) test-types

