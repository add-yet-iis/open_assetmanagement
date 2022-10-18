import csv
import os
import pandas
from .models import Device, Product, ProductSupplier


def handle_uploaded_file(f):
    """
    Handle the uploaded csv or Excel file.
    If it's a csv send directly to csv_to_device else convert to csv first.

    :param f: Uploaded File.
    :type f: Bytestream

    """
    d_loc = '/tmp/'
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


def csv_to_device(filename, delimiter=','):
    """
    This function adds data from the given csv file to the database

    :param filename: The filename of the csv to be imported
    :type filename: str
    :param delimiter: The seperator of the csv file. The default is ','
    :type delimiter: char
    """
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
            try:
                version = row['version']
            except KeyError:
                version = ""
            try:
                type = row['type']
            except KeyError:
                type = ""
            product, exists = Product.objects.get_or_create(
                product_supplier_id=supplier,
                model=product_model,
                version=version,
                type=type,
            )
            if 'eos' in row and not row['eos'] == "":
                product.endOfSupport=row['eos']
            product.save()
            try:
                serial = row['serial_number']
            except KeyError:
                serial = ""
            device, exists = Device.objects.update_or_create(
                device_name=row['name'],
                defaults={
                    'product_id': product,
                    'serial_number': serial,
                    'csv_import': True,
                },
            )
            if 'os' in row and not row['os'] == "":
                device.os = row['os']
            if 'auto' in row:
                device.automatic_import = True
            if 'mac' in row and not row['mac'] == "":
                device.mac_address = row['mac']
            if 'ip' in row and not row['ip'] == "":
                device.ip_address = row['ip']
            device.save()


def xlsx_to_csv(d_loc, d_name, d_name_csv):
    """
    This function converts an Excel file to a csv file using the module pandas

    :param d_loc: The directory where the file is located
    :type d_loc: str
    :param d_name: The filename of the xlsx file to be converted
    :type d_name: str
    :param d_name_csv: The filename of the csv file to be created
    :type d_name: str
    """
    try:
        read_file = pandas.read_excel(d_loc + d_name)
        read_file.to_csv(d_loc + d_name_csv, index = None, header=True)
    except:
        pass
    return d_loc+d_name_csv


def csv_to_xlsx(d_loc, d_name, d_name_xlsx):
    """
    This function converts a csv file to an Excel file (.xlsx) using the module pandas

    :param d_loc: The directory where the file is located
    :type d_loc: str
    :param d_name: The filename of the csv file to be converted
    :type d_name: str
    :param d_name_xlsx: The filename of the xlsx file to be created
    :type d_name: str
    """
    read_file = pandas.read_csv(d_loc + d_name)
    read_file.to_excel(d_loc + d_name_xlsx, index=None, header=True)