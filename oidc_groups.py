from django.contrib.auth.models import Group


def oidc_groups_handler(strategy, response, user, *args, **kwargs):
    # clone groups from LDAP
    groups = Group.objects.filter(name__in=response["groups"])
    user.groups.add(*groups)

    # give active rtps superuser and staff
    is_active_rtp = "active_rtp" in response["groups"]
    user.is_superuser = is_active_rtp
    user.is_staff = is_active_rtp

    strategy.storage.user.changed(user)
