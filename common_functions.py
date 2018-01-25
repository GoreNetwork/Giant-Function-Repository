import os
import re
import socket
import sys
import netmiko
from getpass import getpass
from ciscoconfparse import CiscoConfParse
from pprint import pprint

#Pull MAC addresses from input
def get_mac (input):
	return(re.findall(r'(?:[0-9a-fA-F].?){12}', input))

#Pull IP addresses from input
def get_ip (input):
	return(re.findall(r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)', input))

#Read in document, and turn each line into an entry in a list
def read_doc_list (file_name):
	doc = []
	for line in open(file_name, 'r').readlines():
		doc.append(line)
	return doc

#Delete/re-create the doc and write varable to it
def to_doc_w(file_name, varable):
	f=open(file_name, 'w')
	f.write(varable)
	f.close()	

#Append data to doc	
def to_doc_a(file_name, varable):
	f=open(file_name, 'a')
	f.write(varable)
	f.close()	

#Removes "remove_this" and everything before it from a line
def remove_start(line,remove_this):
	line_search = re.search(remove_this,line)
	line = line[line_search.end()+1:]
	return line

#Uses Netmiko to make a connection, trys SSH then Telnet.  If it failes it writes an error to "Issues.csv"	
def make_connection (ip,username,password):
	try:
		return netmiko.ConnectHandler(device_type='cisco_ios', ip=ip, username=username, password=password)
	except:
		try:
			return netmiko.ConnectHandler(device_type='cisco_ios_telnet', ip=ip, username=username, password=password)
		except:
			issue = ip+ ", can't be ssh/telneted to"
			to_doc_a("Issues.csv", issue)
			to_doc_a("Issues.csv", '\n')
			return None

#Finds all entries of "text" in file (or a list) 
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
	
def remove_start(line,remove_this):
	line_search = re.search(remove_this,line)
	line = line[line_search.end():]
	return line

#NSlookup IP to get FQDN	
def pull_dns_from_ip(input):
	print (input)
	nslookup = socket.getfqdn(str(input))
	return nslookup

#Runs command on the netmiko session and returns the result
def run_command (net_connect, command):
	return net_connect.send_command_expect(command)
