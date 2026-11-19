from users.models import Group, Owner, OwnerGroup

def csh_oidc_handler(strategy, response, user, *args, **kwargs):
    # mirror groups
    groups = [
        Group.objects.get_or_create(name=group)[0] for group in response["groups"]
    ]

    user.groups.set(groups)

    owner, _ = Owner.objects.get_or_create(
        name=user.username,
        defaults={"group": OwnerGroup.objects.get_or_create(name="Members")[0]},
    )

    if not owner.users.filter(pk=user.pk).exists():
        owner.users.set([user])

    # give active rtps superuser and staff
    is_active_rtp = "active_rtp" in response["groups"]
    user.is_superuser = is_active_rtp
    user.is_staff = is_active_rtp

    user.is_active = "member" in response["groups"]

    # save
    strategy.storage.user.changed(user)
