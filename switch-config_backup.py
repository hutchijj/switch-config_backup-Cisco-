
import Crypto
import paramiko

tftp_server = input('TFTP server: ')
local_file = input('Local Filename: ')
remote_file = input('File name on TFTP server: ')


def valid_ip(potential_ip):
	'''
	Checks to see if an IP address is valid.
	
	Returns either True or False
	
	taken from a lesson by CCIE emeritus Kirk Byers (https://pynet.twb-tech.com/) class Python for Network Engineers
	
	'''	

	octets = potential_ip.split('.')
	if len(octets) != 4:
		return False
		
	for i, octet in enumerate(octets):
		try:
			octets [i] = int(octet)
		except ValueError:
			return False
	
	first, second, third, fourth = octets
	if first < 1 or first > 223 or first == 127:
		return False
		
	if first == 169 and second == 254:
		return False

	for octet in (second, third, fourth):
		if octet < 0 or octet > 255:
			return False
			
	else:
		return True
		
def dev_commands():
#sends listed commands via send_string_and_wait_for_string to the device connected to via dev_connect

	send_string_and_wait_for_string("conf t\n", "(config)#", False)
	send_string_and_wait_for_string("file prompt quiet\n", "(config)#", False)
	send_string_and_wait_for_string("end\n", "#", False)
	send_string_and_wait_for_string(r"copy flash:/" + local_file + r" tftp://" + tftp_server + r"/" + switch['hostname'] + ".txt\n", "#", True)
	send_string_and_wait_for_string("conf t\n", "(config)#", True)
	send_string_and_wait_for_string("file prompt alert\n", "(config)#", False)
	send_string_and_wait_for_string("end\n", "#", False)
	#closes SSH session
	client.close()
	
def send_string_and_wait_for_string(command, wait_string, should_print):
#sends the 'command' parameter to the device and collects an output buffer if needed for logging purposes
#function adapted from the work of Tim Mattison, found on his blog at http://blog.timmattison.com/archives/2014/06/25/automating-cisco-switch-interactions/

    # Send the su command
    shell.send(command)

    # Create a new receive buffer
    receive_buffer = ""

    while not wait_string in receive_buffer:
        # Flush the receive buffer
        receive_buffer += str(shell.recv(1024))

    # Print the receive buffer, if necessary
    if should_print:
        print(receive_buffer)

    return receive_buffer

with open(r'c:\switch_ips.csv','r') as f:
	for line in f:
		switch = {}
		switch_line = line.split(',')
		switch = {
			'ip':switch_line[0],
			'username':switch_line[1],
			'password':switch_line[2],
			'hostname' = str(switch_line[3]).strip('\n')
			}
		if valid_ip(switch['ip']) and switch['password'] and switch['username']:
			# Create an SSH client
			client = paramiko.SSHClient()
			# Make sure that we add the remote server's SSH key automatically
			client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			# Connect to the client
			client.connect(switch['ip'], username = switch['username'], password =switch['password'], allow_agent=False, look_for_keys = False)
			# Create a raw shell
			shell = client.invoke_shell()
			# Wait for the prompt
			send_string_and_wait_for_string("", "#", False)
			# Disable more and primes the receive_buffer in send_string_and_wait_for_string
			send_string_and_wait_for_string("terminal length 0\n", "#", True)
	
			#Sends the commands within the dev_commands function, then closes the connection
			dev_commands()
		else:
			print('No dice')

#Joshua Hutchins 2016
