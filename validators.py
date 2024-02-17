from extras.validators import CustomValidator

class DNSValidator(CustomValidator):
    def validate(self, instance):
        from netbox_dns.models import Record, RecordTypeChoices
        if instance.type == RecordTypeChoices.AAAA:
            records = Record.objects.filter(name=instance.name, zone=instance.zone, type=RecordTypeChoices.A)
            if records.exists() and records[0].ipam_ip_address.assigned_object_id != instance.ipam_ip_address.assigned_object_id:
                self.fail("iPv4 Record for this name exists on a different interface!", field='name')
                return
            records = Record.objects.filter(name=instance.name, zone=instance.zone, type=RecordTypeChoices.CNAME)
            if records.exists():
                self.fail("Record for this name in this zone already exists!", field='name')
                return
        if instance.type == RecordTypeChoices.A:
            records = Record.objects.filter(name=instance.name, zone=instance.zone, type=RecordTypeChoices.AAAA)
            if records.exists() and records[0].ipam_ip_address.assigned_object_id != instance.ipam_ip_address.assigned_object_id:
                self.fail("iPv6 Record for this name exists on a different interface!", field='name')
                return
            records = Record.objects.filter(name=instance.name, zone=instance.zone, type=RecordTypeChoices.CNAME)
            if records.exists():
                self.fail("Record for this name in this zone already exists!", field='name')
                return
        if instance.type == RecordTypeChoices.CNAME:
            records = Record.objects.filter(name=instance.name, zone=instance.zone, type__in=[RecordTypeChoices.A, RecordTypeChoices.AAAA])
            if records.exists():
                self.fail("Record for this name in this zone already exists!", field='name')
                return
        records = Record.objects.filter(name=instance.name, zone=instance.zone, type=instance.type)
        if records.exists():
            self.fail("Record of given type for this name in this zone already exists!", field='name')
            return

