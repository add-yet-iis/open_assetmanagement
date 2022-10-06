# from .models import Device, Product, ProductSupplier
# import filehandler
import os
import nmap

RANGE = "10.0.0.0/24"


def initial_netdiscover():
    os.system('netdiscover -r ' + RANGE + '> ndout.txt')
    # os.system('rm ndout.txt')


def crackmapexec():
    os.system('crackmapexec smb ' + RANGE + '> cme.txt')
    # os.system('rm cme.txt')


def nmap_discovery():
    nm = nmap.PortScanner()
    nm.scan('10.0.0.0/28', '22-500')
    for host in nm.all_hosts():
        ssh_info = ""
        try:
            ssh_info = nm[host]['tcp'][22]['version'].split(" ")[1]
        except:
            pass
        print('Host : %s (%s) %s' % (host, nm[host].hostname(), ssh_info))

    nm.scan(hosts='10.0.0.0/28', arguments='-sV -O')
    print()
def network_discovery():
    os.system('whoami')
    os.system('sudo cat /etc/passwd')
    # initial_netdiscover()
    # crackmapexec()
    nmap_discovery()


network_discovery()
