FROM python:3.8-buster

LABEL maintainer="Cláudio Pereira <supernova@claudiop.com>"

# Could copy everything here instead of just pip-packages,
# but this way is better for development as source changes do not affect cached image layers
COPY pip-packages /
RUN apt update \
&& apt install  -y --no-install-recommends sqlite libgdal20 \
&& pip install --no-cache-dir --trusted-host pypi.python.org -r /pip-packages \
&& rm -rf /var/lib/apt/lists/* /pip-packages

VOLUME  ["/conf", "/http"]
WORKDIR /source
EXPOSE 1893
ENTRYPOINT ["gunicorn", "-c", "/conf/gunicorn.conf.py", "asgi:application", "-k", "uvicorn.workers.UvicornWorker"]
COPY . /
