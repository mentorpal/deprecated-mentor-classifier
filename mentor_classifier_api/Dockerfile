FROM python:3.8 as builder
WORKDIR /build
RUN pip install poetry
COPY mentor_classifier ./mentor_classifier
# build mentor-classifier as something api can install
RUN cd mentor_classifier \
	&& poetry config virtualenvs.create false \
	&& poetry install --no-dev \
	&& poetry build
FROM python:3.8-slim
ENV STATUS_URL_FORCE_HTTPS=false
# for now we need to pre install 
# cpu-only versions of all the torch pip modules.
# The problem stmes from that fb doesn't publish 
# the cpu versions to pypi and then versions of pip
# after 19.0 don't respect "dependency_links"
# (e.g. for https://download.pytorch.org/whl/torch_stable.html)
# in setup.py
RUN pip3 install \
	torch==1.9.0+cpu \
	torchvision==0.10.0+cpu \
	-f https://download.pytorch.org/whl/torch_stable.html
ENV FLASK_APP=mentor_classifier_api
WORKDIR /app
RUN pip install poetry
WORKDIR /app/mentor_classifier
# the only thing we need from mentor_classifier is the built .gz (to install)
COPY --from=builder /build/mentor_classifier/dist ./dist
WORKDIR /app
RUN cd mentor_classifier_api \
	&& poetry config virtualenvs.create false \
	&& poetry install --no-dev \
	&& pip uninstall -y poetry
COPY src .
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
