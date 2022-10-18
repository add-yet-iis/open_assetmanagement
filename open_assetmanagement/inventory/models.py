from django.db import models
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.forms.models import model_to_dict


class ProductSupplier(models.Model):
    name = models.CharField(max_length=255)
    contact_information = models.TextField(blank=True, null=True)
    acquisitionHistory = models.TextField(blank=True, null=True)
    supportContracts = models.TextField(blank=True, null=True)
    additionalInformation = models.TextField(blank=True, null=True)

    def __str__(self):
            return self.name


class Product(models.Model):
    product_supplier_id = models.ForeignKey(ProductSupplier, on_delete=models.CASCADE)
    model = models.CharField(max_length=255)
    version = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=255, blank=True)
    endOfSupport = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.model


class Device(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    device_name = models.CharField(max_length=255, blank=True, unique=True)
    serial_number = models.CharField(max_length=255, blank=True)
    mac_address = models.CharField(max_length=255, default="", blank=True)
    ip_address = models.GenericIPAddressField(default="0.0.0.0", blank=True, null=True)
    os = models.CharField(max_length=255, blank=True)
    automatic_import = models.BooleanField(default=False)
    csv_import = models.BooleanField(default=False)
    group = models.CharField(max_length=255, blank=True)
    network = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    redundancy = models.TextField(blank=True)
    role = models.TextField(blank=True)
    interdependencies = models.TextField(blank=True)
    criticality = models.TextField(blank=True)
    configuration_file = models.TextField(blank=True)

    def __str__(self):
        return self.device_name

    def values(self):
        return model_to_dict(self, fields=[field.name for field in self._meta.fields]).values()

    def keys(self):
        return model_to_dict(self, fields=[field.name for field in self._meta.fields]).keys()

    class CommunicationCapability(models.TextChoices):
        NO_COMMUNICATION = 'NO', _('No communication')
        LOCAL = 'LO', _('Local communication only')
        EXTERNAL = 'EX', _('External Communication')

    communication_capability = models.CharField(
        max_length=2,
        choices=CommunicationCapability.choices,
        default=CommunicationCapability.NO_COMMUNICATION,
        blank=True,
    )


class Software(models.Model):
    product_supplier_id = models.ForeignKey(ProductSupplier, on_delete=models.CASCADE)
    device_id = models.ForeignKey(Device, on_delete=models.CASCADE)
    software_name = models.CharField(max_length=255)
    software_version = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=255, blank=True)
    endOfSupport = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.software_name

    class CommunicationCapability(models.TextChoices):
        NOCOMMUNICATION = 'NO', _('No communication')
        LOCAL = 'LO', _('Local communication only')
        EXTERNAL = 'EX', _('External Communication')
    communication_capability = models.TextField(
        choices=CommunicationCapability.choices,
        default=CommunicationCapability.NOCOMMUNICATION,
        blank=True,
    )
