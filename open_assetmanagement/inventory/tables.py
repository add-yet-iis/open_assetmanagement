import django_tables2 as tables
from .models import *
from django_tables2.utils import Accessor  # alias for Accessor


class ProductTable(tables.Table):
    class Meta:
        model = Product
        exclude = ()
        DJANGO_TABLES2_TEMPLATE = "django_tables2/bootstrap4.html"


class DeviceTable(tables.Table):
    device_name = tables.LinkColumn("inventory:device", text=lambda device: device.device_name, args=[Accessor("pk")])
    product = tables.LinkColumn("inventory:product", text=lambda device: device.product_id, args=[Accessor("product_id.pk")], order_by="product_id.model")
    supplier = tables.LinkColumn("inventory:supplier", text=lambda device: device.product_id.product_supplier_id, args=[Accessor("product_id.product_supplier_id.pk")], order_by="product_id.product_supplier_id.name")
    product_id__version = tables.Column(verbose_name="Version", default="")
    product_id__type = tables.Column(verbose_name="Typ", default="")
    # type = models.CharField(max_length=255, blank=True)
    # endOfSupport = models.DateField(blank=True, null=True)
    id = tables.Column(visible=False)
    csv_import = tables.Column(visible=False)
    automatic_import = tables.Column(visible=False)

    class Meta:
        model = Device
        sequence = ("device_name", "supplier", "product", "product_id__version", "product_id__type", )
        exclude = ("product_id", )
        attrs = {
            "id": "assets",
            "class": "table-striped table-hover table table-bordered text-nowrap display",
            "th": {
                "class": ""
            },
            "li": {
                "class": "page-item"
            },
        }
        row_attrs = {
            'class': lambda record: 'table-danger' if record.automatic_import else ('table-warning' if record.csv_import else ''),
        }
        DJANGO_TABLES2_TEMPLATE = "django_tables2/bootstrap4.html"
