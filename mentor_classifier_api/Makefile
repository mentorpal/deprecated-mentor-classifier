BLACK_EXCLUDES="/(\.venv|build)/"
DOCKER_IMAGE?=mentor-classifier-api
DOCKER_IMAGE_ID=$(shell docker images -q ${DOCKER_IMAGE} 2> /dev/null)
ROOT=$(shell dirname ${PWD})
MENTOR_CLASSIFIER_SRC=$(ROOT)/mentor_classifier
VENV=.venv

$(VENV):
	$(MAKE) install

.PHONY: install
install: poetry-ensure-installed
	cd $(ROOT)/mentor_classifier \
		&& $(MAKE) poetry-build-classifier
	poetry config --local virtualenvs.in-project true
	poetry env use python3.8
	poetry install

.PHONY: deps-show
deps-show:
	poetry show

.PHONY: deps-show
deps-show-outdated:
	poetry show --outdated

.PHONY: deps-update
deps-update:
	poetry update

.PHONY clean:
clean:
	rm -rf .venv .pytest_cache .mypy_cache build

build/mentor_classifier:
	mkdir -p build
	rsync -rv \
			--exclude .venv \
			--exclude htmlcov \
			--exclude .pytest_cache \
			--exclude tests \
			--exclude __pycache__ \
		$(MENTOR_CLASSIFIER_SRC) build
	
.PHONY docker-build:
# docker-build: clean build/mentor_classifier
docker-build: clean
	cd .. \
		&& docker build  --no-cache -t $(DOCKER_IMAGE) -f ./mentor_classifier_api/Dockerfile .


.PHONY docker-build:
docker-run:
	docker run \
		-it \
		--rm \
		-p 5000:5000 \
	$(DOCKER_IMAGE)

.PHONY: format
format: $(VENV)
	cd $(ROOT) && $(MAKE) format

.PHONY: license
license:
	cd $(ROOT) && make license

.PHONY: test
test: $(VENV)
	cd $(ROOT)/shared/ && $(MAKE) installed/word2vec.bin
	cd $(ROOT)/shared/ && $(MAKE) installed/sentence-transformer
	cd $(ROOT)/shared/ && $(MAKE) installed/pop_culture.csv
	cd $(ROOT)/shared && $(MAKE) installed/spacy-model
	poetry run coverage run \
		--omit="$(PWD)/tests $(VENV)" \
		-m py.test -vv $(args)

.PHONY: test-all
test-all:
	$(MAKE) test-format
	$(MAKE) test-lint
	$(MAKE) test-license
	$(MAKE) test-types
	$(MAKE) test

.PHONY: test-format
test-format: $(VENV)
	cd $(ROOT) && $(MAKE) test-format

.PHONY: test-license
test-license:
	cd $(ROOT) && make test-license
	
.PHONY: test-lint
test-lint: $(VENV)
	cd $(ROOT) && $(MAKE) test-lint

.PHONY: test-types
test-types: $(VENV)
	cd $(ROOT) && $(MAKE) test-types

.PHONY: poetry-ensure-installed
poetry-ensure-installed:
	sh $(ROOT)/tools/poetry_ensure_installed.sh
