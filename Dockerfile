FROM python:3.9-buster

LABEL maintainer="Cláudio Pereira <supernova@claudiop.com>"

# Could copy everything here instead of just pip-packages,
# but this way is better for development as source changes do not affect cached image layers
COPY pip-packages /
RUN apt update \
&& DEBIAN_FRONTEND=noninteractive apt install  -y --no-install-recommends sqlite libgdal20 locales \
&& pip install --no-cache-dir --trusted-host pypi.python.org -r /pip-packages \
&& rm -rf /var/lib/apt/lists/* /pip-packages \
&& sed -i -e 's/# pt_PT.UTF-8 UTF-8/pt_PT.UTF-8 UTF-8/' /etc/locale.gen \
&& dpkg-reconfigure --frontend=noninteractive locales \
&& update-locale LANG=pt_PT.UTF-8

VOLUME  ["/conf", "/http"]
WORKDIR /source
EXPOSE 1893
ENTRYPOINT ["gunicorn", "-c", "/conf/gunicorn.conf.py", "asgi:application", "-k", "uvicorn.workers.UvicornWorker"]
COPY . /
