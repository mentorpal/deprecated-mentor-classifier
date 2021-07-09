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
ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
RUN rm /tmp/requirements.txt
COPY build /tmp/build
RUN pip install /tmp/build/mentor_classifier
RUN rm -rf /tmp/build
ENV FLASK_APP=mentor_classifier_api
WORKDIR /app
COPY src .
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
