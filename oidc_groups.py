from django.contrib.auth.models import Group


def oidc_groups_handler(strategy, response, user, *args, **kwargs):
    # mirror groups
    #groups = [
    #    Group.objects.get_or_create(name=group)[0] for group in response["groups"]
    #]
    #user.groups.set(groups)

    # give active rtps superuser and staff
    is_active_rtp = "active_rtp" in response["groups"]
    user.is_superuser = is_active_rtp
    user.is_staff = is_active_rtp

    user.is_active = "member" in response["groups"]

    # save
    strategy.storage.user.changed(user)
