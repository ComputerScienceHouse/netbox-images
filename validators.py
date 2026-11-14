from extras.validators import CustomValidator

class DNSValidator(CustomValidator):
    def validate(self, instance, request):
        from netbox_dns.models import Record
        from netbox_dns.choices import RecordTypeChoices
        from django.contrib import messages

        messages.info(request, instance)

        otherRecords = Record.objects.filter(name=instance.name, zone=instance.zone)

        # Exclude the same instance from these queries, we have to do this so that SOA stuff works
        if instance.pk:
            otherRecords = otherRecords.exclude(pk=instance.pk)

        if instance.type == RecordTypeChoices.AAAA:
            records = otherRecords.filter(type=RecordTypeChoices.A)
            if records.exists() and records[0].ipam_ip_address.assigned_object_id != instance.ipam_ip_address.assigned_object_id:
                self.fail("iPv4 Record for this name exists on a different interface!", field='name')
            records = otherRecords.filter(type=RecordTypeChoices.CNAME)
            if records.exists():
                self.fail("Record for this name in this zone already exists!", field='name')

        if instance.type == RecordTypeChoices.A:
            records = otherRecords.filter(type=RecordTypeChoices.AAAA)
            if records.exists() and records[0].ipam_ip_address.assigned_object_id != instance.ipam_ip_address.assigned_object_id:
                self.fail("iPv6 Record for this name exists on a different interface!", field='name')
            records = otherRecords.filter(type=RecordTypeChoices.CNAME)
            if records.exists():
                self.fail("Record for this name in this zone already exists!", field='name')

        if instance.type == RecordTypeChoices.CNAME:
            records = otherRecords.filter(type__in=[RecordTypeChoices.A, RecordTypeChoices.AAAA])
            if records.exists():
                self.fail("Record for this name in this zone already exists!", field='name')

        records = otherRecords.filter(type=instance.type)

        messages.info(request, records)

        if records.exists():
            self.fail("Record of given type for this name in this zone already exists!", field='name')

