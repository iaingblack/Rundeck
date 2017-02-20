#!/usr/bin/python

#  USEFUL LINKS
#    http://rundeck.org/docs/administration/managing-node-sources.html#using-properties
#    name, hostname, os-name, os-version, os-family, os-arch, username, description, tags, project

#/var/rundeck/Scripts/ResourceModelSource/zabbix-source.py zabbixhost machinename username zabbixapiuser zabbixapipassword
from pyzabbix import ZabbixAPI
import yaml
import sys

#Returns all the hostgroups a host is part of
def getHostsHostgroups(host):
    hostGroupTags = []
    hostGroupString = ""
    #Get hostgroups host is a member of and add as tags
    for items in zapi.host.get(filter={"host": str(host)}, selectGroups="extend", output="hostid"):
        zbxHostGroups=items['groups']
        for hostgroupname in zbxHostGroups:
            hostGroupTags.append(str(hostgroupname['name']))
        hostGroupString = ",".join(hostGroupTags)
    return hostGroupString

#Get the Macros a host has
def getHostsMacros(hostid):
    hostsMacros = zapi.usermacro.get(hostids=hostid, output="extend")
    return hostsMacros

#Get a hostgroups hosts
def getHostgroupHosts(hostgroup):
    # Get all  hosts in group we looked for
    result = zapi.hostgroup.get(name=hostgroup, output="extend")
    for items in result:
        if (str(items['name'].upper())) == (hostgroup.upper()):
            return zapi.host.get(groupids=items['groupid'], output="extend")
    return None

#HOST QUERY
def getHost(hostname):
    result = zapi.host.get(filter={'host' :[zabbix_item]}, output="extend")
    return result

#START OF PROGRAM
if len(sys.argv) != 7:
    print("  Needs to be 6 items.  Use like this;")
    print("  get_zabbix-source.py zabbixserver[1] (zabbix server FQDN) zabbix_host[2] host_username[3] zabbixusername[4] zabbixpassword[5] osFamily[6]")
    print("  ie python zabbix-source.py machinename.domain.local \"myservername\" serverusername rundeck rundeck Windows/Unix")
    quit()

# The Zabbix server URL, hostgroup, host username and zabbix API credentials to use
zabbix_server = "http://"+sys.argv[1]+"/zabbix/"
zabbix_item = sys.argv[2]
host_username=(sys.argv[3]).upper()
zapi = ZabbixAPI(zabbix_server)
zapi.login(sys.argv[4], sys.argv[5])
osFamily=sys.argv[6]
# Variables we need to look for and use
hostsJson = {}
osFamily = ""
groupid="-1"
#=================================================================
#Look for a host with this name first (case sensitive)
result = getHost(zabbix_item)
if len(result) <> 1:
    result = getHostgroupHosts(zabbix_item)
    if result == None:
        print("Not found host or hostgroup, quitting")
        quit()

#Now go through each host and build the required JSON for Rundeck
for items in result:
    # Get only first part of string in case name has extra descriptive text - Like "myservername (dev server)"
    hostname = ((items['name']).split()[0])
    #Create basic JSON object for Rundeck node
    hostdetails = {'name': str(hostname), 'hostname': str(hostname),
                   'username': str(host_username), 'osFamily': osFamily, 'tags': getHostsHostgroups(hostname)}
    #Get any macros that are added to the host and apply them to the JSON object
    hostsMacros = getHostsMacros(items['hostid'])
    if len(hostsMacros) > 0:
        macrosJson = {}
        #Build a list of macros in the host to append to the host
        for macros in hostsMacros:
            #Check all combinations. Add as required to this list. This is not exhaustive so far
            if "RUNDECK_USERNAME" in (macros['macro'].upper()):
                hostdetails.update({"username": str(macros['value'])})
            if "RUNDECK_SSHPASSWORDSTORAGEPATH" in (macros['macro'].upper()):
                hostdetails.update({"ssh-key-storage-path": str(macros['value'])})
            if "RUNDECK_OSFAMILY" in (macros['macro'].upper()):
                hostdetails.update({"osFamily": str(macros['value'])})
            if "RUNDECK_OSNAME" in (macros['macro'].upper()):
                hostdetails.update({"osName": str(macros['value'])})
            if "RUNDECK_DESCRIPTION" in (macros['macro'].upper()):
                hostdetails.update({"description": str(macros['value'])})
            if "RUNDECK_NODENAME" in (macros['macro'].upper()):
                hostdetails.update({"nodename": str(macros['value'])})
            if "RUNDECK_HOSTNAME" in (macros['macro'].upper()):
                hostdetails.update({"hostname": str(macros['value'])})

    hostsJson.update({str(hostname): hostdetails})

output = yaml.dump(hostsJson, default_flow_style=False)
print(output)
quit()
