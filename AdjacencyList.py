import paramiko
import sys
import time
import re

mgtIP = sys.argv[1:len(sys.argv)]
noDevices = len(mgtIP)

client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

adjNode = {}
details = {}
port_type=''
deviceType = ''

for ip in mgtIP:
    client.connect(ip, username='exam', password='exam',look_for_keys=False,allow_agent=False)
    stdin, stdout, stderr = client.exec_command("show running-config | include hostname")
    hostname = stdout.readlines()
    hostname = hostname[0].encode('utf-8').rstrip().split(' ')[1]
    #hostname = hostname.split(' ')[1]
    adjNode[ip] = {'Local-Hostname':hostname, 'Adjacent-Node':[]}
    #adjNode[ip]={hostname:{}}
    client.connect(ip, username='exam', password='exam',look_for_keys=False,allow_agent=False)
    stdin, stdout, stderr = client.exec_command("show cdp entry *")
    output = stdout.readlines()
    output = [x.encode('utf-8').rstrip() for x in output]
    #client.close()
    for line in output:
        if("Device ID" in line):
            adjHost = line.split(':')[1]
            details['Adjacent-Host-Name'] = adjHost
            #adjacentNode[ip][hostname].update({'Adjacent-Node Hostname':adjHost})
        elif("Capabilities" in line):
            match = re.search("Capabilities:.*",line)
            match = match.group()
            deviceType = match.split(':')[1][1:]
            #details['Device-Type']=deviceType
            if(deviceType == "Router"):
                adjVlan = "N/A"
                details['Adj-Native-VLAN']='N/A'
                details['Adjacent-Allowed-VLANs']='N/A'
            
        elif("Interface" in line):
            localInterface = line.split(',')[0].split(':')[1]
            adjInterface = line.split(',')[1].split(':')[1]
            details['Local-Interface']=localInterface
            details['Adjacent-Interface']=adjInterface
            client.connect(ip, username='exam', password='exam',look_for_keys=False,allow_agent=False)
            stdin, stdout, stderr = client.exec_command("show interfaces " + localInterface + " switchport | include Administrative")
            output = stdout.readlines()
            output = [x.encode('utf-8').rstrip() for x in output]
            #print("Output command: ", output[0])
            if("trunk" not in output[0]):
                client.connect(ip, username='exam', password='exam',look_for_keys=False,allow_agent=False)
                stdin, stdout, stderr = client.exec_command("show interfaces " + localInterface + " switchport | include Access")            
                localVlan = stdout.readlines()
                localVlan = [x.encode('utf-8').rstrip() for x in localVlan]
                localVlan = localVlan[0].split(':')[1].split(' ')[1]
                details['Local-VLAN']=localVlan
                port_type='access'
                details['Allowed-VLANs']='N/A'
            else:
                client.connect(ip, username='exam', password='exam',look_for_keys=False,allow_agent=False)
                stdin, stdout, stderr = client.exec_command("show interfaces " + localInterface + " switchport | include Trunking")
                output = stdout.readlines()
                output = [x.encode('utf-8').rstrip() for x in output]
                match = re.search('\d.*',output[-1])
                if(match):
                    allowedVLANs = match.group() 
                details['Allowed-VLANs']=allowedVLANs
                port_type = "Trunk"
                client.connect(ip, username='exam', password='exam',look_for_keys=False,allow_agent=False)
                stdin, stdout, stderr = client.exec_command("show interfaces " + localInterface + " switchport | include Access")            
                localVlan = stdout.readlines()
                localVlan = [x.encode('utf-8').rstrip() for x in localVlan]
                localVlan = localVlan[0].split(':')[1].split(' ')[1]
                details['Local-VLAN']=localVlan
                #allowedVLANs=''
            #adjacentNode[ip].update({'Local-Interface':localInterface,'Adjacent-Interface':adjInterface})
            #break;
        elif("Native VLAN" in line):
            output = line.split(':')[1]
            #print(output)
            match = re.search('\d+',output)
            adjVlan = match.group()
            if(deviceType!="Router"):
                details['Adj-Native-VLAN']=adjVlan
            else:
                details['Adj-Native-VLAN']='N/A'
            #print("Port-type",port_type)
            if(port_type=="Trunk"):
                details['Adjacent-Allowed-VLANs']=allowedVLANs
            else:
                details['Adjacent-Allowed-VLANs']='N/A'
        elif("Management address(es)" in line):
            adjNode[ip]['Adjacent-Node'].append(details)
            details = {}
        else:
            continue
    #client.connect(ip, username='exam', password='exam',look_for_keys=False,allow_agent=False)
    #stdin, stdout, stderr = client.exec_command("show interfaces " + localInterface + " switchport | include Access")
    #localVlan = stdout.readlines()
    #localVlan = [x.encode('utf-8').rstrip() for x in localVlan]
    #localVlan = localVlan[0].split(':')[1].split(' ')[1]
    
    #adjacentNode[ip].update({'Local-VLAN':localVlan})

#print(adjNode)
#print("length of adjacent nodes: ", len(adjNode['192.168.1.2']['Adjacent-Node']))

for ip in mgtIP:
    print "Device Management IP: ",ip
    print "Hostname: ", adjNode[ip]['Local-Hostname']
    for i in range(len(adjNode[ip]['Adjacent-Node'])):
        print "Neighbor " + str(i+1) + " details:"
        print "\tAdjacent Host name: ", adjNode[ip]['Adjacent-Node'][i]['Adjacent-Host-Name']
        print "\tLocal Interface: ", adjNode[ip]['Adjacent-Node'][i]['Local-Interface']
        print "\tAdjacent Node Interface: ", adjNode[ip]['Adjacent-Node'][i]['Adjacent-Interface']
        print "\tLocal VLAN: ",adjNode[ip]['Adjacent-Node'][i]['Local-VLAN']
        print "\tAdjacent Native VLAN: ",adjNode[ip]['Adjacent-Node'][i]['Adj-Native-VLAN']
        print "\tAllowed VLANs: ", adjNode[ip]['Adjacent-Node'][i]['Allowed-VLANs']
        print "\tAdjacent Allowed VLANs: ", adjNode[ip]['Adjacent-Node'][i]['Adjacent-Allowed-VLANs']
        
 
