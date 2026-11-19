# CSH Netbox
OKD Containers for CSH's Netbox instance, now with CSH SSO!

## Running locally (for working on scripts?)

Copy `.env.example` to `.env` and fill in the values

If you would like to operate with the real data, copy `.env-remote-netbox.exmaple` to `.env-remote-netbox`.
Then start the postgres database `podman compose up postgres`, and exec the dump script `podman exec postgres sh -c /sync-local-db.sh`

Run the compose file
`podman compose up --build`

### Scripts
Scripts in the `./scripts` directory get built into the `/opt/netbox/custom-scripts` folder as well as `/opt/netbox/netbox/scripts` folder. 
The `custom-scripts` folder is used as a local datasource within netbox, and then the `/opt/netbox/netboxo/scripts` is where it all gets put, this is to ensure consistency across workers.
See [https://netboxlabs.com/docs/netbox/customization/custom-scripts/](https://netboxlabs.com/docs/netbox/customization/custom-scripts/) for info on writing custom scripts

## Upgrading

First, pause rollouts to all netbox deployments in OKD:

```
kubectl rollout pause deployment/netbox-app -n netbox
kubectl rollout pause deployment/netbox-static -n netbox
kubectl rollout pause deployment/netbox-rqworker -n netbox
```

Then, try something like:
```
git -C netbox pull
git add netbox
git commit -m "netbox: bump to $(grep '^VERSION = ' netbox/netbox/netbox/settings.py | awk '{print $3}' | sed "s/'//g")"
git push
```

When the build finishes, we need to run database migrations:

```
kubectl create -n netbox -f migrate.yaml
```

Wait for the job to finish and complete.

When it's finished, you can unpause rollouts:

```
kubectl rollout resume deployment/netbox-app -n netbox
kubectl rollout resume deployment/netbox-static -n netbox
kubectl rollout resume deployment/netbox-rqworker -n netbox
```

I _think_ that's it?
[Sorry if these instructions suck](https://cshrit.slack.com/archives/C055T9WP3/p1656377635896189)
