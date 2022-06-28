# CSH Netbox
OKD Containers for CSH's Netbox instance, now with LDAP!

## Upgrading

First, pause rollouts to all netbox deployments in OKD.

Then, try something like:
```
git -C netbox pull
git add netbox
git commit -m "netbox: bump to $(grep '^VERSION = ' netbox/netbox/netbox/settings.py | awk '{print $3}' | sed "s/'//g")"
git push
```

When the build finishes, we need to run database migrations:

```
kubectl create -n netbox migrate.yaml
```

I _think_ that's it?
[Sorry if these instructions suck](https://cshrit.slack.com/archives/C055T9WP3/p1656377635896189)
