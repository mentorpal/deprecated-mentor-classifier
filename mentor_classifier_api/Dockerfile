FROM python:3.8 as builder
WORKDIR /build
COPY mentor_classifier ./mentor_classifier
# build mentor-classifier as something api can install
RUN cd mentor_classifier \
    && pip install jsonschema \
	&& pip install poetry \
	&& poetry config virtualenvs.create false \
	&& poetry install --no-dev \
    && pip install poethepoet \
	&& poetry run poe force-cpu-only \
	&& poetry build \
    && poetry cache clear $(poetry cache list) --all -n \
    # seems like poetry and pip caches
    # are not clearing no matter what so hacking with below...
    && rm -rf /root/.cache/* \
    && pip uninstall -y poetry poethepoet
FROM python:3.8-slim
ENV STATUS_URL_FORCE_HTTPS=false
# for now we need to pre install
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
ENV FLASK_APP=mentor_classifier_api
WORKDIR /app/mentor_classifier
# the only thing we need from mentor_classifier is the built .gz (to install)
COPY --from=builder /build/mentor_classifier/dist ./dist
WORKDIR /app
COPY mentor_classifier_api ./mentor_classifier_api
RUN cd mentor_classifier_api \
    && pip install jsonschema \
    && pip install poetry \
	&& poetry config virtualenvs.create false \
	&& poetry install --no-dev \
    && pip install poethepoet \
	&& poetry run poe force-cpu-only \
	&& poetry cache clear $(poetry cache list) --all -n \
    # seems like poetry and pip caches
    # are not clearing no matter what so hacking with below...
    && rm -rf /root/.cache/* \
    && pip uninstall -y poetry poethepoet
COPY mentor_classifier_api/src .
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
