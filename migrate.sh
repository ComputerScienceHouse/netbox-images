#!/bin/bash -ex

# These shouldn't be run automatically by us
# We package these so they can be run by a human
python3 netbox/manage.py migrate
python3 netbox/manage.py trace_paths --no-input
python3 netbox/manage.py remove_stale_contenttypes --no-input
python3 netbox/manage.py reindex --lazy
python3 netbox/manage.py clearsessions
python3 netbox/manage.py clearcache
