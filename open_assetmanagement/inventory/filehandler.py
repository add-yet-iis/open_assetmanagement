import csv
from .models import Device, Product, ProductSupplier


def handle_uploaded_file(f):
    d_loc = 'inventory/'
    print(f.name)
    if "csv" in str.lower(f.name):
        d_name = 'tmp.csv'
        is_csv = True
    else:
        d_name = 'tmp.xlsx'
        is_csv = False
    with open(d_loc + d_name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    if is_csv:
        csv_to_device(d_loc + d_name)
    else:
        pass


def csv_to_device(filename):
    with open(filename) as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            supplier, exists = ProductSupplier.objects.get_or_create(
                name=row['supplier'],
            )
            product, exists = Product.objects.get_or_create(
                product_supplier_id=supplier,
                model=row['model'],
                version=row['version'],
                type=row['type'],
                endOfSupport=row['eos'],
            )
            device, exists = Device.objects.update_or_create(
                product_id=product,
                device_name=row['name'],
                serial_number=row['serial_number'],
            )
            print(device)
