# Use a clean Arch Linux base install as the parent of this image 
# This is good for development, but might not fit production
FROM archlinux/base

LABEL maintainer="Cláudio Pereira <development@claudiop.com>"

# Install required system packages.
# gcc:         GCC (required to compile uwsgi)
# python:      Pretty much everything
# python-pip:  Dependencies
# sqlite:      Read vulnerability database
# gdal:        Geographical extensions
# git:         Server version determination
# After finished, 
RUN pacman -Sy gcc python python-pip sqlite gdal git --noconfirm --noprogressbar --cachedir /tmp

# Install pip packages
COPY pip-packages /usr/src/
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r /usr/src/pip-packages  && rm /usr/src/pip-packages

# Uninstall compiler & dependencies. Cleanup cleanup cache, doc's, man entries and unused locales.
RUN pacman -Rns gcc --noconfirm --noprogressbar

# Put the source in place
COPY source /supernova/source
# Tag exports
VOLUME  ["/supernova/config", "/srv/http/supernova"]
# Change directory into it
WORKDIR /supernova
# Expose the uwsgi port
EXPOSE 1893

ENV SN_CONFIG /supernova/config/settings.json
ENV PYTHONUNBUFFERED 1

# Execute uwsgi daemon once this container runs
ENTRYPOINT ["uwsgi", "config/uwsgi.ini"]
