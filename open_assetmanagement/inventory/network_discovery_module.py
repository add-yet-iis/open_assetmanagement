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

# Format of CME Discoveries
# discovered = {
#     "ip": {
#         "os": "os",
#         "supplier": "supplier",
#         "mac": "mac",
#         "ports": "ports"
#     }
# }

# Format of NMAP Discoveries
# discovered = {
#     "ip": {
#         "os": "os",
#         "supplier": "supplier",
#         "mac": "mac",
#         "ports": "ports"
#     }
# }


def crackmapexec(scanning_range):
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
    print(discovered)
    return discovered


def nmap_discovery(scanning_range):
    nm = nmap.PortScanner()
    discovered = {}
    try:
        nm.scan(hosts=scanning_range, arguments='-sV -O')
        print("SUDO POWER !")
        for host in nm.all_hosts():
            entry = {
                "os": "",
                "supplier": "",
                "mac": "",
                "ports": ""
            }
            ssh_info = ""
            try:
                entry['os'] = nm[host]['osmatch'][0]['name'] + " " + nm[host]['osmatch'][0]['accuracy'] + "%"
            except:
                pass
            try:
                entry['mac'] = nm[host]['addresses']['mac']
            except:
                pass
            try:
                ssh_info = nm[host]['tcp'][22]['version'].split(" ")[1]
            except:
                pass
            try:
                entry['supplier'] = ssh_info + nm[host]['vendor'][entry['mac']]
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
                entry['supplier'] = nm[host]['tcp'][22]['version'].split(" ")[1]
            except:
                pass
            discovered.update({host: entry})
    return discovered


def dict_to_csv(dict_data):
    a_file = open("network_discovery.csv", "w")

    writer = csv.writer(a_file)
    for key, value in dict_data.items():
        writer.writerow([key, value])

    a_file.close()
    return a_file


def network_discovery(scan_range):
    # Start with NMAP Scan. Will run nmap -sV -O if run as sudo. (Highly recommended)
    # data_nmap = nmap_discovery(scan_range)

    # Accurate OS Info from SMB Scan (Windows only)
    data_cme = crackmapexec(scan_range)

    # Add the CME Data to the Nmap Data
    # data = data_combine(data_cme, data_nmap)

    # Convert found Data to csv
    #data_csv = dict_to_csv(data)
    # Return csv to be imported by the filehandler into database
    #return data_csv


network_discovery(RANGE)
