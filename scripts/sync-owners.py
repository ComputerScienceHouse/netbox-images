from extras.scripts import *

class SyncOwnersScript(Script):
  class Meta(Script.Meta):
    name = "Sync Owners via LDAP"

  test_hi = StringVar(
    description="Name of test"
  )

  def run(self, data, commit):
    self.log_success(f"test script ran with name {data['test_hi']}")
