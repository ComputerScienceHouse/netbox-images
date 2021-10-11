FROM docker.io/python:3.9-slim

EXPOSE 8080

RUN apt update
RUN apt install -y python3 \
  python3-wheel \
  build-essential \
  libxml2-dev \
  libxslt1-dev \
  libffi-dev \
  libpq-dev \
  libssl-dev \
  zlib1g-dev

COPY netbox/requirements.txt /opt/netbox/requirements.txt
RUN pip install django-storages
RUN pip install -r /opt/netbox/requirements.txt

COPY netbox /opt/netbox

COPY configuration.env.py /opt/netbox/netbox/netbox/configuration.py
COPY gunicorn.py /opt/netbox/gunicorn.py
COPY migrate.sh /opt/netbox/migrate.sh

WORKDIR /opt/netbox

# Adapted from upgrade.sh
RUN python3 netbox/manage.py collectstatic --no-input

USER 1069

ENTRYPOINT [ "gunicorn", "--config", "/opt/netbox/gunicorn.py", "--pythonpath", "/opt/netbox/netbox", "netbox.wsgi" ]
