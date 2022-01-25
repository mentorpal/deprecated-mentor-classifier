FROM python:3.8-slim as builder
# To use celery over AWS SQS requires pycurl
# and it doesn't work unless it's compiled,
# which requires hundreds of MB of build tools...
# So we do a two-phase docker build.
# In the first phase, we compile pycurl
# as a wheel, and then in the final phase,
# we install from that wheel (to avoid needing the build tools)
RUN apt-get update && \
    apt-get install -y \
        build-essential \
        libcurl4-openssl-dev \
        libssl-dev \
    && pip install wheel \
    && pip wheel \
            --wheel-dir=/svc/wheels \
            --no-binary :all: \
            --global-option="--with-openssl" \
            --no-cache-dir \
        pycurl
FROM python:3.8-slim
WORKDIR /app
COPY poetry.lock pyproject.toml ./
COPY mentor_classifier mentor_classifier
COPY mentor_classifier_tasks mentor_classifier_tasks
RUN ls -la
RUN pip install poetry \
    && pip install jsonschema \
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
COPY --from=builder /svc /svc
# install pycurl the way kombu/sqs needs it
RUN apt-get update && \
    apt-get install -y \
        libcurl4-openssl-dev \
        libssl-dev \
    && pip uninstall pycurl \
    && pip install --no-index --find-links=/svc/wheels pycurl \
    && rm -rf /var/lib/apt/lists/*
COPY bin/training_worker.sh .
RUN chmod a+x training_worker.sh
ENTRYPOINT ["mentor_classifier"]
CMD [ "train" ]