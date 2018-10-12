# SNM - Adjacency List

This application gets a list of Management IP addresses of Cisco Switches and opens up an SSH connection to each of these devices using the Python Paramiko module. The application then extracts the information about all of the device's adjacent nodes using Cisco CLI commands. The information about all the devices is stored in a dictionary and could be retrieved using Key-Value pair. 

Dependencies: 
paramiko - To install this module, use the following command:
pip install Paramiko

How to run:

1. Set up a topology consisting of switches and routers with interconnections between them.
2. Configure the Switches with VLANs and Trunk links. 
3. Configure the switches with Management IPs. 
4. Connect one of the switches with the host that will be launching this application.
5. Configure the host with an IP that's in the subnet as the Switches.
6. Run the following command to execute the program:
  python AdjacencyList.py <list_of_mgt_address>
