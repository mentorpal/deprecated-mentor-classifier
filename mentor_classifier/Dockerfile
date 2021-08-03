FROM python:3.8-slim
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
# WORKDIR /opt/mentor_classifier
# COPY . .
WORKDIR /app
COPY poetry.lock pyproject.toml ./
COPY mentor_classifier mentor_classifier
COPY mentor_classifier_tasks mentor_classifier_tasks
RUN ls -la
RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev \
    && pip install poethepoet \
    && poetry run poe force-cpu-only \
    && poetry cache clear $(poetry cache list) --all -n \
    && pip uninstall -y poetry poethepoet
# RUN rm -rf /opt/mentor_classifier
COPY mentor_classifier_tasks .
COPY bin/training_worker.sh .
RUN chmod a+x training_worker.sh
ENTRYPOINT ["mentor_classifier"]
CMD [ "train" ]