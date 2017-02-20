#!/usr/bin/python
# /var/rundeck/Scripts/ResourceModelSource/manual-source.py machinename domainname.local windows username
import yaml
import sys

if len(sys.argv) != 5:
    print("  Needs to be 5 items.  Use like this;")
    print("  manual-source.py server_name[1] domain[2] (domainname or workgroup) os_type[3] host_username[4]")
    print("  ie python manual-source.py machinename domainname.local windows username")
    quit()


# Variables we need to look for and use
allowed_os = {'WINDOWS', 'LINUX'}

hostsJson = {}
hostname = (sys.argv[1]).upper()
domain   = (sys.argv[2]).upper()
osFamily = (sys.argv[3]).upper()
username = (sys.argv[4]).upper()
hostnamefqdn = ""

if (osFamily not in allowed_os):
    print("Has to be one of these OSs;")
    print("".join([str(" - "+x+"\n") for x in allowed_os]))
    quit()

#I know this is nasty but people might get confused with UNIX. So, just prompting with LINUX and overriding it
if (osFamily == "LINUX"):
    osFamily = "UNIX"

if (domain == "WORKGROUP"):
    hostnamefqdn = hostname
else:
    hostnamefqdn = hostname + "." + domain
    hostname = hostnamefqdn
    username = username+"@"+domain

hostdetails = {'name': hostname, 'hostname': hostnamefqdn,
              'username': username, 'osFamily': osFamily}

thishost = {str(hostname): hostdetails}
hostsJson.update({str(hostname): hostdetails})

output = yaml.dump(hostsJson, default_flow_style=False)
print(output)
quit()
