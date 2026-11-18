from extras.scripts import *
from utilities.exceptions import AbortScript

from users.models import Owner, OwnerGroup, User
from tenancy.models import Tenant, TenantGroup

from os import environ as env, name

from csh_ldap import CSHLDAP

class SyncOwnersScript(Script):
  class Meta(Script.Meta):
    name = "Sync Owners via LDAP"

  target_group = StringVar(
      required = False
      )

  def setupLDAP(self):
    bind_dn = env.get('NETBOX_LDAP_BIND_DN', '')
    bind_pw = env.get('NETBOX_LDAP_BIND_PW', '')

    if bind_dn == '':
      raise AbortScript("Configuration Error, enviornment varilable 'NETBOX_LDAP_BIND_DN' not found")

    if bind_pw == '':
      raise AbortScript("Configuration Error, enviornment varilable 'NETBOX_LDAP_BIND_PW' not found")

    return CSHLDAP(bind_dn, bind_pw)

  def run(self, data, commit):
    ldap = self.setupLDAP()

    target_group = data.get('target_group', 'current_student')

    if target_group == '': target_group = 'current_student'

    self.log_info(f"group is {target_group}")

    members = ldap.get_group_member_attributes(groups=[target_group],attributes=['uid', 'nsAccountLock'])

    tenantMemberGroup = TenantGroup.objects.get(name='Member')

    memberGroup = OwnerGroup.objects.get(name='Members')

    existingOwners = set(Owner.objects.values_list('name', flat=True).distinct())

    existingTenants = set(Tenant.objects.values_list('name', flat=True).distinct())

    memberUsernames = ldap.get_group_member_uids(groups=[target_group])

    users = {u.username: u for u in User.objects.filter(username__in=memberUsernames)}

    for memberDict in members:
      member = memberDict['uid']
      enabled = memberDict.get('nsAccountLock', 'False').lower() == 'false'

      if not enabled:
        if member in existingOwners:
          owner = Owner.objects.get(name=member)
          owner.delete()

          if member in users:
            user = users.get(member)
            user.active = False
            user.full_clean()
            user.save()

          self.log_info(f"Removing owner for deactivated account {member}")
        continue

      if member not in existingOwners:
        owner = Owner(
            name=member,
            group=memberGroup
        )

        self.log_info(f"Creating owner for user {member}")
      else: 
        owner = Owner.objects.get(name=member)

      if member in users:
        owner.users.set([users[member]])

      owner.full_clean()
      owner.save()

      if not member in existingTenants:
        tenant = Tenant(
            name=member,
            slug=member,
            group=tenantMemberGroup
        )

        tenant.full_clean()
        tenant.save()

    self.log_success(f"Script ran with no errors")
