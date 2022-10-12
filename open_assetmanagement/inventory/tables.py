import django_tables2 as tables
from .models import Device
from django_tables2.utils import Accessor  # alias for Accessor


class DeviceTable(tables.Table):
    device_name = tables.LinkColumn("inventory:device", text=lambda device: device.device_name, args=[Accessor("pk")])
    product_id = tables.LinkColumn("inventory:product", text=lambda device: device.product_id, args=[Accessor("product_id.pk")])

    class Meta:
        model = Device
        template_name = "django_tables2/bootstrap4.html"

