FROM python:3.8-slim
WORKDIR /app
COPY poetry.lock pyproject.toml ./
COPY mentor_classifier mentor_classifier
COPY mentor_classifier_tasks mentor_classifier_tasks
RUN ls -la
RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev \
    && pip install poethepoet \
    # for now we need force install
    # cpu-only versions of all the torch pip modules.
    # The problem stmes from that fb doesn't publish
    # the cpu versions to pypi and then versions of pip
    # after 19.0 don't respect "dependency_links"
    # (e.g. for https://download.pytorch.org/whl/torch_stable.html)
    # in setup.py
    # RUN pip3 install \
    # 	torch==1.9.0+cpu \
    # 	torchvision==0.10.0+cpu \
    # 	-f https://download.pytorch.org/whl/torch_stable.html
    && poetry run poe force-cpu-only \
    && poetry cache clear $(poetry cache list) --all -n \
    # seems like poetry and pip caches
    # are not clearing no matter what so hacking with below...
    && rm -rf /root/.cache/* \
    && pip uninstall -y poetry poethepoet
COPY bin/training_worker.sh .
RUN chmod a+x training_worker.sh
ENTRYPOINT ["mentor_classifier"]
CMD [ "train" ]