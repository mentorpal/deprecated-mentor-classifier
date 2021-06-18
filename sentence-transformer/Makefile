ROOT=$(shell dirname ${PWD})
VENV=.venv
$(VENV):
	$(MAKE) $(VENV)-update

.PHONY: $(VENV)-update
$(VENV)-update: venv-activate
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r ./requirements.txt

.PHONY clean:
clean:
	rm -rf .venv distilbert-base-nli-mean-tokens 

.PHONY: update-deps
update-deps: $(VENV)
	. $(VENV)/bin/activate && pip-upgrade requirements*

venv-activate:
	python3 -m venv $(VENV)

sentence_transformer: $(VENV)
	. $(VENV)/bin/activate && python transformer_download.py
