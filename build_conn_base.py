#Everything you need to read in a list of IPs, and pull the username/password

from common_functions import *
from getpass import getpass

ips_doc = "IPs.txt"
username = input("Username: ")
password = getpass()
ips = []
for line in read_doc (ips_doc):
	temp_ips = get_ip (line)
	for temp_ip in temp_ips:
		ips.append(temp_ip)
	



