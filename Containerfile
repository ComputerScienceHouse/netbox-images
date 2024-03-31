FROM docker.io/python:3.10-slim

EXPOSE 8080

RUN apt-get update && \
  apt-get install -y build-essential \
  libxml2-dev \
  libxslt1-dev \
  libffi-dev \
  libpq-dev \
  libssl-dev \
  zlib1g-dev \
  libldap2-dev \
  libsasl2-dev \
  libssl-dev

COPY netbox/requirements.txt /opt/netbox/requirements.txt
COPY local_requirements.txt /opt/netbox/local_requirements.txt
RUN pip install django-storages django-auth-ldap srvlookup
RUN pip install -r /opt/netbox/requirements.txt
RUN pip install -r /opt/netbox/local_requirements.txt

COPY netbox /opt/netbox
COPY oidc_groups.py /opt/netbox/netbox/oidc_groups.py

COPY configuration.env.py /opt/netbox/netbox/netbox/configuration.py
COPY ldap_config.env.py /opt/netbox/netbox/netbox/ldap_config.py
COPY gunicorn.py /opt/netbox/gunicorn.py
COPY migrate.sh /opt/netbox/migrate.sh


WORKDIR /opt/netbox

RUN NETBOX_SECRET_KEY="6l0~ZBT9yFIQoZxak9H=N_f6~@Yhbu~YS4s6r8-R2%GwXZVV)0" mkdocs build && \
  NETBOX_SECRET_KEY="6l0~ZBT9yFIQoZxak9H=N_f6~@Yhbu~YS4s6r8-R2%GwXZVV)0" \
  python3 netbox/manage.py collectstatic --no-input

USER 1069

ENTRYPOINT [ "gunicorn", "--config", "/opt/netbox/gunicorn.py", "--pythonpath", "/opt/netbox/netbox", "netbox.wsgi" ]
