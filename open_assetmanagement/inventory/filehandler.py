import csv
import os
import pandas
from .models import Device, Product, ProductSupplier


def handle_uploaded_file(f):
    d_loc = 'inventory/tmp/'
    print(f.name)
    if "csv" in str.lower(f.name):
        d_name = 'import.csv'
        is_csv = True
    else:
        d_name = 'import.xlsx'
        is_csv = False
    with open(d_loc + d_name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    if is_csv:
        csv_to_device(d_loc + d_name, ";")
        os.remove(d_loc + d_name)
    else:
        path_to_csv = xlsx_to_csv(d_loc, d_name, 'import.csv')
        print(path_to_csv)
        csv_to_device(path_to_csv, ",")
        os.remove(d_loc + d_name)
        os.remove(path_to_csv)


def csv_to_device(filename, delimiter):
    with open(filename, encoding="utf8", errors="ignore") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            try:
                sup_name = row['supplier']
                if sup_name == "":
                    sup_name = "Unbekannt"
            except KeyError:
                sup_name = "Unbekannt"
            supplier, exists = ProductSupplier.objects.get_or_create(
                    name=sup_name,
            )
            try:
                product_model = row['model']
            except KeyError:
                product_model = "Unbekannt"
            product, exists = Product.objects.get_or_create(
                product_supplier_id=supplier,
                model=product_model,
                version=row['version'],
                type=row['type'],
                endOfSupport=row['eos'],
            )
            device, exists = Device.objects.update_or_create(
                device_name=row['name'],
                defaults={
                    'product_id': product,
                    'serial_number': row['serial_number'],
                    'csv_import': True,
                },
            )


def xlsx_to_csv(d_loc, d_name, d_name_csv):
    try:
        read_file = pandas.read_excel(d_loc + d_name)
        read_file.to_csv(d_loc + d_name_csv, index = None, header=True)
    except:
        pass
    return d_loc+d_name_csv


def csv_to_xlsx(d_loc, d_name, d_name_xlsx):
    read_file = pandas.read_csv(d_loc + d_name)
    read_file.to_excel(d_loc + d_name_xlsx, index=None, header=True)