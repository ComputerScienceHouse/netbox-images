import os
import srvlookup
import random
import logging

import ldap
from ldap.ldapobject import ReconnectLDAPObject
from django_auth_ldap.config import LDAPSearch, LDAPGroupType

def __discover_ldap__():
  ldap_srvs = srvlookup.lookup("ldap", "tcp", "csh.rit.edu")
  ldap_uris = ['ldaps://' + uri.hostname for uri in ldap_srvs]
  random.shuffle(ldap_uris)
  server_uri = None
  con = None
  for uri in ldap_uris:
    try:
      con = ReconnectLDAPObject(uri)
      server_uri = uri
      con.unbind()
      break
    except (ldap.SERVER_DOWN, ldap.TIMEOUT):
      continue

  return server_uri


# Server URI
AUTH_LDAP_SERVER_URI = __discover_ldap__()

# Set the DN and password for the NetBox service account.
AUTH_LDAP_BIND_DN = os.environ.get("NETBOX_LDAP_BIND_DN")
AUTH_LDAP_BIND_PASSWORD = os.environ.get("NETBOX_LDAP_BIND_PW")

# Include this setting if you want to ignore certificate errors. This might be needed to accept a self-signed cert.
# Note that this is a NetBox-specific setting which sets:
#     ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
LDAP_IGNORE_CERT_ERRORS = False

AUTH_LDAP_USER_FLAGS_BY_GROUP = {
  "is_active": "cn=member,cn=groups,cn=accounts,dc=csh,dc=rit,dc=edu",
  "is_staff": "cn=rtp,cn=groups,cn=accounts,dc=csh,dc=rit,dc=edu",
  "is_superuser": "cn=rtp,cn=groups,cn=accounts,dc=csh,dc=rit,dc=edu"
}

AUTH_LDAP_USER_SEARCH = LDAPSearch(
  "cn=users,cn=accounts,dc=csh,dc=rit,dc=edu",
  ldap.SCOPE_SUBTREE,
  "(uid=%(user)s)"
)

AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
  "cn=groups,cn=accounts,dc=csh,dc=rit,dc=edu",
  ldap.SCOPE_SUBTREE
  # ,"(objectClass=posixgroup)"
)

logger = logging.getLogger("django_auth_ldap")

class IPAGroupType(LDAPGroupType):
  def user_groups(self, ldap_user, group_search):
    """
    Searches for any group that is either the user's primary or contains the
    user as a member.
    """
    logger.debug("Is in groups?")

    groups = []

    try:
      user_dn = ldap_user.attrs["dn"][0]

      filterstr = "(member={})".format(
        self.ldap.filter.escape_filter_chars(user_dn)
      )

      search = group_search.search_with_additional_term_string(filterstr)
      groups = search.execute(ldap_user.connection)
    except (KeyError, IndexError):
      logger.exception("shit")
      pass

    logger.debug("User's groups: " + str(groups))

    return groups

  def is_member(self, ldap_user, group_dn):
    """
    Returns True if the group is the user's primary group or if the user is
    listed in the group's memberUid attribute.
    """
    logger.debug("Is Member? " + ldap_user.attrs["uid"][0])
    try:
      for membership in ldap_user.attrs["memberOf"]:
        if membership == group_dn:
          return True
    except (KeyError, IndexError):
      logger.warn("Exception reached in checking membership for " +
                  ldap_user.attrs["uid"][0] + " in " + group_dn)
      logger.warn(ldap_user.attrs)

    return False


AUTH_LDAP_GROUP_TYPE = IPAGroupType()

AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,cn=users,cn=accounts,dc=csh,dc=rit,dc=edu"

AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenname",
    "last_name": "sn",
    "email": "mail"
}

# Mirror LDAP group assignments.
AUTH_LDAP_MIRROR_GROUPS = True

# For more granular permissions, we can map LDAP groups to Django groups.
AUTH_LDAP_FIND_GROUP_PERMS = True

# Cache groups for one hour to reduce LDAP traffic
AUTH_LDAP_CACHE_TIMEOUT = 3600
