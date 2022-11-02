"""
This module is an example for a module that could extend the asset-management tool.
It collects data on assets in the network with the tools nmap and crackmapexec and sends this data to the filehandler
in the form of a csv file

"""

import nmap
import subprocess
import pandas as pd

RANGE = "10.0.0.0/24"
CME_SMB = "\x1b[1m\x1b[34mSMB\x1b[0m"
CME_STAR = "\x1b[1m\x1b[34m[*]\x1b[0m"
INTERFACE = "eth1"
# WARNING ! POTENTIAL SHELL INJECTION VIA RANGE ! FILTER FILTER FILTER

# Format of Discoveries
# discovered = {
#    "ip": {
#       "name": "",
#       "os": "",
#       "supplier": "",
#       "mac": "",
#       "ports": "",
#       "network": scanning_range,
#       "domain": "",
# }
# }


def initial_netdiscover(scan_range: str, active=False, timeout: int = 300):
    """ This function performs an ARP Scan via the command-line tool netdiscover and returns the data as a dictionary

    :param timeout: This parameter describes how long the netdiscover scan should run for in seconds. Default is 300
    :param scan_range: 192.168.0.0/24, 192.168.0.0/16 or 192.168.0.0/8. Currently, acceptable ranges are /8,
    /16 and /24 only
    :param active: Enable active mode. In passive mode, netdiscover does not send anything, but does only sniff
    :return:
    """
    discovered = {}
    if not active:
        process = subprocess.Popen(['sudo', 'timeout', str(timeout), 'netdiscover', '-r', scan_range, '-i', INTERFACE, '-PNp'],
                               stdout=subprocess.PIPE)
    else:
        process = subprocess.Popen(['sudo', 'netdiscover', '-r', scan_range, '-i', INTERFACE, '-PN'],
                                   stdout=subprocess.PIPE)
    out, err = process.communicate()
    for line in out.decode("utf-8").splitlines():
        line = line.split(maxsplit=4)
        if not line:
            return discovered
        discovered.update({
            line[0]: {
                "supplier": line[4],
                "mac": line[1],
                "auto": True,
                "name": line[0] + "-NameUnknown",
                "network": scan_range
            }
        })
    return discovered


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
            "smb_v1": os_info[4],
            "network": scanning_range
        }
        discovered.update({ip_and_name[0]: entry})
    return discovered


def nmap_discovery(scanning_range: str, discovered=None, syn=False, full=False) -> dict[str, dict[str, str]]:
    """
    Discovers Assets with the command-line-tool nmap and returns them in a Dict

    :param full: Do a full scan. Scanns all ports
    :param discovered: Already discovered hosts
    :param syn: Use Syn Scan. Scans the top 100 ports with Stealth-Syn Scan
    :param scanning_range: str IP Range of Network to be scanned
    :return: Discovered Data
    :rtype: dict[str, dict[str, str]]
    """
    if discovered is None:
        discovered = {}
    nm = nmap.PortScanner()
    discovered = discovered
    try:
        if syn:
            nm.scan(hosts=scanning_range, arguments='-sS --top-ports 100', sudo=True)
        elif full:
            nm.scan(hosts=scanning_range, arguments='-sS -sV -p- -T4', sudo=True)
        else:
            nm.scan(hosts=scanning_range, arguments='-sV -O', sudo=True)

        for host in nm.all_hosts():
            entry = {
                "name": "",
                "os": "",
                "supplier": "",
                "mac": "",
                "ports": "",
                "auto": True,
                "network": scanning_range,
                "domain": "",
            }
            ssh_info = ""
            try:
                entry['name'] = nm[host]['hostnames'][0]['name']
                if not entry['name']:
                    entry['name'] = host + "-NameUnknown"
            except:
                entry['name'] = host + "-NameUnknown"
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
            try:
                software = []
                for proto in nm[host].all_protocols():
                    ports = nm[host][proto].keys()
                    for port in ports:
                        print(port)
                        print(nm[host][proto][port])
                        sw = {
                            "port": port,
                            "name": str(nm[host][proto][port]["name"]) + " - " + str(nm[host][proto][port]["product"]),
                            "version": nm[host][proto][port]["version"],
                            "full": nm[host][proto][port],
                        }
                        software.append(sw)
                print(software)
                entry.update({"software": software})
            except:
                print("error in sw")
            discovered.update({host: entry})
    except:
        print("No root!")
    return discovered


def data_combine(data_cme: dict, data_nmap: dict) -> object:
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
            if "Linux" not in data_nmap[host]['os']:
                data_nmap[host]['os'] = data_cme[host]['os']
            data_nmap[host]['name'] = data_cme[host]['name']
            data_nmap[host].update({'domain': data_cme[host]['domain']})
            data_nmap[host].update({'smb_signing': data_cme[host]['smb_signing']})
            data_nmap[host].update({'smb_v1': data_cme[host]['smb_v1']})
        except KeyError:
            # Not found -> Add host to data.
            data_nmap.update({host: data_cme[host]})
    return data_nmap


def s7_discovery(scan_range: str):
    discovered = {}
    nm = nmap.PortScanner()
    try:
        nm.scan(hosts=scan_range, arguments='--script s7-info.nse -p 102 ', sudo=True)

        filtered_hosts = []
        for host in nm.all_hosts():
            if nm[host]['tcp'][102]['state'] in 'open':
                filtered_hosts.append(host)

        for host in filtered_hosts:

            entry = {
                "name": nm[host]['hostnames'][0]['name'] if not nm[host]['hostnames'][0]['name'] == "" else "PLC-" + str(host),
                "os": "",
                "supplier": "Siemens",
                "mac": nm[host]['addresses']['mac'],
                "ports": "102",
                "type": "PLC",
                "auto": True,
                "network": scan_range,
                "model": nm[host]['tcp'][102]['product'] + " - " +
                         nm[host]['tcp'][102]['script']['s7-info'].splitlines()[1].replace("Module: ", "").strip(),
                "version": nm[host]['tcp'][102]['script']['s7-info'].splitlines()[3].replace("Version: ", "").strip(),
                "serial_number": nm[host]['tcp'][102]['script']['s7-info'].splitlines()[5].replace("Serial Number: ", "").strip()
            }
            discovered.update({host: entry})
    except:
        print("No root!")

    # noinspection PyArgumentList
    pd.DataFrame(discovered).T.reset_index(names="ip").to_csv('s7_discovery.csv', index=False)
    return 's7_discovery.csv'


def network_discovery(scan_range: str, level: int, timeout: int) -> str:
    """
    This is the Function to call when a network discovery is wanted. It returns Data as CSV for further processing by
    the filehandler. It is an example of a module to expand the asset management DB and Webapp

    :param timeout: Timeout for netdiscover
    :param level: Scanning Intensity. 0 - passive Netdiscover, 1 - SYN Scan, 2 - OS Scan
    :param scan_range: str IP Range of Network to be scanned
    :return: CSV to be handled
    """

    # Level (very) Careful = Netdiscover Scan! Needs Sudo Privileges
    data = initial_netdiscover(scan_range, bool(level), timeout)
    if level == 2:
        # Level 2 Medium - SYN Scan
        data = nmap_discovery(scan_range, data, syn=True)
    elif level == 3:
        # Level 3 Os Scan
        # Start with NMAP Scan. Will run nmap -sV -O if run as sudo. (Highly recommended) and return a Dict
        data_nmap = nmap_discovery(scan_range, data)

        # Accurate OS Info from SMB Scan (Windows only) returned as Dict
        data_cme = crackmapexec(scan_range)

        # Add the CME Data to the Nmap Data
        data = data_combine(data_cme, data_nmap)
    elif level == 4:
        # Level 4 Full Port Scan
        data = nmap_discovery(scan_range, data, full=True)

    # Convert found Data to csv
    # noinspection PyArgumentList
    pd.DataFrame(data).T.reset_index(names="ip").to_csv('network_discovery.csv', index=False)

    # Return csv filename to be imported by the filehandler into database
    return 'network_discovery.csv'