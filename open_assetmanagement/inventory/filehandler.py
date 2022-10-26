import csv
import os
import pandas
from .models import Device, Product, ProductSupplier, Software
from ast import literal_eval


def handle_uploaded_file(f, delimiter=','):
    """
    Handle the uploaded csv or Excel file.
    If it's a csv send directly to csv_to_device else convert to csv first.

    :param delimiter: Defines the Delimiting Character of the CSV-File
    :param f: Uploaded File.
    :type f: Bytestream

    """
    d_loc = '/tmp/'
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
        csv_to_device(d_loc + d_name, delimiter)
        os.remove(d_loc + d_name)
    else:
        path_to_csv = xlsx_to_csv(d_loc, d_name, 'import.csv')
        csv_to_device(path_to_csv, delimiter)
        os.remove(d_loc + d_name)
        os.remove(path_to_csv)


def csv_to_device(filename, delimiter=','):
    """
    This function adds data from the given csv file to the database
    The accepted column-names are:
    supplier, model, version, type, eos, serial_number, name, os, auto, mac, ip, network, group
    :param filename: The filename of the csv to be imported
    :type filename: str
    :param delimiter: The seperator of the csv file. The default is ','
    :type delimiter: char
    """
    with open(filename, encoding="utf8", errors="ignore") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:

            # First we create the supplier, or pass the unknown supplier if the row supplier is not found
            if 'supplier' in row and not row['supplier'] == "":
                sup_name = row['supplier']
            else:
                sup_name = "Unknown"
            supplier, exists = ProductSupplier.objects.get_or_create(
                    name=sup_name,
            )

            # Now we create the Product using the supplier and the rows model, version, type and eos
            if 'model' in row and not row['model'] == "":
                product_model = row['model']
            else:
                product_model = "Unknown"
            if 'version' in row and not row['version'] == "":
                version = row['version']
            else:
                version = "Unknown"
            if 'type' in row and not row['type'] == "":
                type = row['type']
            else:
                type = "Unknown"
            product, exists = Product.objects.get_or_create(
                product_supplier_id=supplier,
                model=product_model,
                version=version,
                type=type,
            )
            if 'eos' in row and not row['eos'] == "":
                product.endOfSupport = row['eos']
            product.save()

            # Finally we create the Device using the columns serial_number, name, os, auto, mac, ip, network, group
            if 'serial_number' in row and not row['serial_number'] == "":
                serial = row['serial_number']
            else:
                serial = ""
            if 'name' in row and not row['name'] == "":
                name = row['name']
            else:
                name = "Auto-Import-"

            device, exists = Device.objects.update_or_create(
                device_name=name,
                defaults={
                    'product_id': product,
                    'serial_number': serial,
                    'csv_import': True,
                },
            )
            if name in "Auto-Import-":
                device.device_name= "Auto-Import-0" + str(device.pk)
            if 'os' in row and not row['os'] == "":
                device.os = row['os']
            if 'auto' in row:
                device.automatic_import = True
            if 'mac' in row and not row['mac'] == "":
                device.mac_address = row['mac']
            if 'ip' in row and not row['ip'] == "":
                device.ip_address = row['ip']
            if 'network' in row and not row['network'] == "":
                device.network = row['network']
            if 'group' in row and not row['group'] == "":
                device.group = row['group']
            device.save()

            if 'software' in row and row['software']:
                for sw in literal_eval(row['software']):
                    print(sw)
                    software, exists = Software.objects.update_or_create(
                        software_name=sw['name'],
                        software_version=sw['version'],
                    )
                    software.devices.add(device)
                    software.ports = sw['port']
                    software.save()


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