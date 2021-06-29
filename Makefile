LICENSE=LICENSE
LICENSE_HEADER=LICENSE_HEADER
VENV=.venv
$(VENV):
	$(MAKE) $(VENV)-update

.PHONY: $(VENV)-update
$(VENV)-update:
	[ -d $(VENV) ] || python3.8 -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r ./requirements.txt

.PHONY clean:
clean:
	rm -rf .venv htmlcov .coverage

.PHONY: docker-build
docker-build:
	cd mentor_classifier && $(MAKE) docker-build
	cd mentor_classifier_api && $(MAKE) docker-build

.PHONY: black
black: $(VENV)
	$(VENV)/bin/black .

.PHONY: format
format:
	$(MAKE) license
	$(MAKE) black

LICENSE:
	@echo "you must have a LICENSE file" 1>&2
	exit 1

LICENSE_HEADER:
	@echo "you must have a LICENSE_HEADER file" 1>&2
	exit 1

.PHONY: license
license: LICENSE LICENSE_HEADER $(VENV)
	. $(VENV)/bin/activate \
		&& python -m licenseheaders -t LICENSE_HEADER -d mentor_classifier/mentor_classifier $(args) \
		&& python -m licenseheaders -t LICENSE_HEADER -d mentor_classifier/mentor_classifier_tasks $(args) \
		&& python -m licenseheaders -t LICENSE_HEADER -d mentor_classifier/tests $(args) \
		&& python -m licenseheaders -t LICENSE_HEADER -d mentor_classifier_api/src $(args) \
		&& python -m licenseheaders -t LICENSE_HEADER -d mentor_classifier_api/tests $(args) \
		&& python -m licenseheaders -t LICENSE_HEADER -d tools $(args) \
		&& python -m licenseheaders -t LICENSE_HEADER -d shared $(args)

.PHONY: test
test:
	cd mentor_classifier && $(MAKE) test
	cd mentor_classifier_api && $(MAKE) test

.PHONY: test-all
test-all:
	$(MAKE) test-format
	$(MAKE) test-lint
	$(MAKE) test-license
	$(MAKE) test-types
	$(MAKE) test

.PHONY: test-format
test-format: $(VENV)
	$(VENV)/bin/black --check .

.PHONY: test-lint
test-lint: $(VENV)
	$(VENV)/bin/flake8 .

.PHONY: test-license
test-license: LICENSE LICENSE_HEADER
	args="--check" $(MAKE) license

.PHONY: test-types
test-types: $(VENV)
	. $(VENV)/bin/activate \
		&& mypy mentor_classifier \
		&& mypy mentor_classifier_api
