"""
network_discovery_module

This module is an example for a module that could extend the assetmanagement tool
It collects data on assets in the network with the tools nmap and crackmapexec and sends this data to the filehandler
in the form of a csv file

"""

# from .models import Device, Product, ProductSupplier
# import filehandler
import csv
import nmap
import subprocess

RANGE = "10.0.0.0/24"
CME_SMB = "\x1b[1m\x1b[34mSMB\x1b[0m"
CME_STAR = "\x1b[1m\x1b[34m[*]\x1b[0m"
# WARNING ! POTENTIAL SHELL INJECTION VIA RANGE ! FILTER FILTER FILTER

# ------ This is probably not useful and will be skipped
# def initial_netdiscover():
#    os.system('netdiscover -r ' + RANGE + '> nd_out.txt')
#    # os.system('rm nd_out.txt')
#Format of NMAP Discoveries
#discovered = {
#    "ip": {
#        "os": "os",
#        "supplier": "supplier",
#        "mac": "mac",
#        "ports": "ports"
#    }
#}
#Format of CME Discoveries
#discovered = {
#    "ip": {
#        "os": "os",
#        "supplier": "supplier",
#        "mac": "mac",
#        "ports": "ports"
#    }
#}


def crackmapexec(scanning_range: str) -> dict[str, dict[str, str]]:
    """
    Discovers Assets with the command-line-tool crackmapexec and returns them in a Dict

    :param scanning_range: str IP Range of Network to be scanned
    :return: Discovered Data
    :rtype: dict[str, dict[str, str]]
    """
    discovered = {}
    for line in subprocess.check_output('crackmapexec smb ' + scanning_range, shell=True).decode("utf-8").splitlines():
        line = line.strip(CME_SMB).split(CME_STAR)
        ip_and_name = line[0].split()
        os_info = line[1].replace(")", "").replace("\x00", "").split("(")
        entry = {
            "os": os_info[0],
            "name": ip_and_name[2],
            "domain": os_info[2],
            "smb_signing": os_info[3],
            "smb_v1": os_info[4]
        }
        discovered.update({ip_and_name[0]: entry})
    return discovered


def nmap_discovery(scanning_range: str) -> dict[str, dict[str, str]]:
    """
    Discovers Assets with the command-line-tool nmap and returns them in a Dict

    :param scanning_range: str IP Range of Network to be scanned
    :return: Discovered Data
    :rtype: dict[str, dict[str, str]]
    """
    nm = nmap.PortScanner()
    discovered = {}
    try:
        nm.scan(hosts=scanning_range, arguments='-sV -O -e eth0')
        print("SUDO POWER !")
        for host in nm.all_hosts():
            entry = {
                "name": "",
                "os": "",
                "supplier": "",
                "mac": "",
                "ports": ""
            }
            ssh_info = ""
            try:
                entry['name'] = nm[host]['hostnames'][0]['name']
            except:
                pass
            try:
                ssh_info = nm[host]['tcp'][22]['version'].split(" ")[1]
            except:
                pass
            try:
                entry['os'] = ssh_info + nm[host]['osmatch'][0]['name'] + " " + nm[host]['osmatch'][0]['accuracy'] + "%"
            except:
                pass
            try:
                entry['mac'] = nm[host]['addresses']['mac']
            except:
                pass
            try:
                entry['supplier'] = nm[host]['vendor'][entry['mac']]
            except:
                pass
            try:
                entry['ports'] = nm[host]['tcp']
            except:
                pass
            discovered.update({host: entry})
    except:
        print("No root!")
        nm.scan(scanning_range)
        for host in nm.all_hosts():
            entry = {
                "os": "",
                "supplier": "",
                "mac": "",
                "ports": ""
            }
            ssh_info = ""
            try:
                entry['os'] = nm[host]['tcp'][22]['version'].split(" ")[1]
            except:
                pass
            discovered.update({host: entry})
    return discovered


def dict_to_csv(dict_data: object) -> object:
    """
    This function converts the used Dict Format to csv

    :return: CSV File containing data
    :type dict_data: object
    """
    a_file = open("network_discovery.csv", "w")

    writer = csv.writer(a_file)
    for key, value in dict_data.items():
        writer.writerow([key, value])

    a_file.close()
    return a_file


def data_combine(data_cme: object, data_nmap: object) -> object:
    """
    This Function combines the Dict Data from the Outputs of the CME and NMAP Scans to one complete Dict

    :param data_cme: CME data output by the cme function
    :param data_nmap: Nmap data output by the nmap function
    :return: Data from the nmap scan combined with the additional data from cme
    """
    for host in data_cme:
        # Search every IP from the CME Data in the NMAP Data
        try:
            # Found -> Update Host. But not the os name for Linux, because its wrong... samba
            if not "Linux" in data_nmap[host]['os']:
                data_nmap[host]['os'] = data_cme[host]['os']
            data_nmap[host]['name'] = data_cme[host]['name']
            data_nmap[host].update({'domain': data_cme[host]['domain']})
            data_nmap[host].update({'smb_signing': data_cme[host]['smb_signing']})
            data_nmap[host].update({'smb_v1': data_cme[host]['smb_v1']})
        except KeyError:
            # Not found -> Add host to data.
            data_nmap.update({host: data_cme[host]})
    return data_nmap


def network_discovery(scan_range: str) -> object:
    """
    This is the Function to call when a network discovery is wanted. It returns Data as CSV for further processing by
    the filehandler. It is an example of a module to expand the asset management DB and Webapp

    :param scan_range: str IP Range of Network to be scanned
    :return: CSV to be handled
    """
    # could be oneliner:
    # return dict_to_csv(data_combine(crackmapexec(scan_range), nmap_discovery(scan_range)))

    # Start with NMAP Scan. Will run nmap -sV -O if run as sudo. (Highly recommended) and return a Dict
    data_nmap = nmap_discovery(scan_range)

    # Accurate OS Info from SMB Scan (Windows only) returned as Dict
    data_cme = crackmapexec(scan_range)

    # Add the CME Data to the Nmap Data
    data = data_combine(data_cme, data_nmap)

    # Convert found Data to csv
    data_csv = dict_to_csv(data)

    # Return csv to be imported by the filehandler into database
    return data_csv


network_discovery(RANGE)
