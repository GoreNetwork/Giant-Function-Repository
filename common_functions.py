import os
import re
import socket
import sys
import netmiko
from getpass import getpass
from ciscoconfparse import CiscoConfParse
from pprint import pprint
import ipaddress
import time
#from common_functions import *

#get time 'Wed Nov  7 13:26:23 2018'
def get_time():
	return time.ctime()

#Turn a string into an IP address, and see if that address is in a list of subnets	
def ip_in_subnet_list(ip, subnets_list):
    address = ipaddress.ip_address(ip)
    for subnet in subnets_list:
        if address in subnet:
            return True
    return False

#Take a text file of subnets, and return a list of subnets (useful with ip_in_subnet_list)	
def get_subnets_from_file(file):
    subnets = []
    raw_subnets = read_doc_list (file)
    for line in raw_subnets:
        line = line.strip()
        subnets.append(ipaddress.ip_network(line, strict=False))
    return (subnets)

#Find parent text that has the child text inside it.  File is a file, or a list	
def find_parent_with_child(parent,child,file):
    parse = CiscoConfParse(file)
    par = parse.find_objects(parent)
    parent_list = []
    for obj in par:
        if obj.re_search_children(child):
            parent_list.append(obj.text)
    return parent_list

#Look at files in the current dir.  See which of them has the passed text in the file name	
def pull_file_names_with_text(text):
	file_list = []
	files = os.listdir()
	for file in files:
		if text in file:
			file_list.append(file)
	return (file_list)

#returns a list of mac addresses pulled from the input	
def get_mac (input):
	return(re.findall(r'(?:[0-9a-fA-F].?){12}', input))

#returns a list of IP addresses pulled from the input		
def get_ip (input):
	return(re.findall(r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)', input))
	
#Read in the content of a doc as a list, each line from the doc is an item in a list	
def read_doc_list (file_name):
	doc = []
	for line in open(file_name, 'r').readlines():
		doc.append(line)
	return doc

#Over write existing document with data from varable	(creates doc if doesn't exist)
def to_doc_w(file_name, varable):
	f=open(file_name, 'w')
	f.write(varable)
	f.close()	

#Append varable to existing document (creates doc if doesn't exist)	
def to_doc_a(file_name, varable):
	f=open(file_name, 'a')
	f.write(varable)
	f.close()	

#Pass text to this to see if it's a phone	
def is_it_a_phone(text):
	if len(re.findall(r'^SEP[0-9a-fA-F]{12}',text)) > 0:
		return True
	return False
	
def make_list_string_with_spaces(list):
	line = str(list)
	line = line.replace("[","")
	line = line.replace("]","")
	line = line.replace(","," ")
	line = line.replace("'"," ")
	return line


#SSH/Telnet to device, if it fails to connect it just puts an error in 'issues.csv' and returns None	
def make_connection(ip, username, password):
	try:
		net_connect = netmiko.ConnectHandler(device_type='cisco_ios', ip=ip, username=username, password=password)
		output = net_connect.send_command_expect("show ver")
		# print (output)
		if "Nexus" in output:
			net_connect.disconnect()
			return netmiko.ConnectHandler(device_type='cisco_nxos', ip=ip, username=username, password=password)
		return net_connect
	except:
		try:
			return netmiko.ConnectHandler(device_type='cisco_ios_telnet', ip=ip, username=username, password=password)
		except:
			issue = ip + ", can't be ssh/telneted to"
			to_doc_a("Issues.csv", issue)
			to_doc_a("Issues.csv", '\n')
			return None

#Finds parent text with child text: If you pass it a running config as the file(as a list), and "nterface" it will return a list of lists
#Each sublist will be the config for an interface
def find_child_text (file, text):
	all = []
	parse = CiscoConfParse(file)
	for obj in parse.find_objects(text):
		each_obj = []
		each_obj.append(obj.text)
		for each in obj.all_children:
			each_obj.append(each.text)
		all.append(each_obj)
	return all

# if there is a hostname of bob.ted.com, and you tell it pass .ted.com as remove this it will return bob	
def remove_end(line,remove_this):
	try:
		line_search = re.search(remove_this,line)
		line = line[:line_search.start()]
		return line
	except:
		return line
		
# if there is a hostname of bob.ted.com, and you tell it pass bob as remove this it will return .ted.com		
def remove_start(line,remove_this):
	try:
		line_search = re.search(remove_this,line)
		line = line[line_search.end():]
		return line
	except:
		return line
	
	
#get FQDN from IP address
def nslookup(input):
	print (input)
	#nslookup = socket.getfqdn(str(input),0,0,0,0)
	nslookup = socket.getfqdn(str(input))
	
	return nslookup

#If you have FQDN and want an IP from it	
def get_ip_from_hostname(hostname):
    return get_ip(str(socket.getaddrinfo(hostname, 80)))[0]

#Pass a command to be run on the SSH/Telnet connection	
def run_command_on_net_connect(net_connect,command):
	return net_connect.send_command_expect(command)

#Get the hostname of the Cisco device you are connected to	
def get_hostname (ssh_connect):
	return ssh_connect.find_prompt()[:-1]

#Pass a command to be run on the SSH/Telnet connection		
def send_command(net_connect,command):
	return net_connect.send_command_expect(command)
