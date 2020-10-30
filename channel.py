"""
Copyright (c) 2019 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

DNAC Onboarding

"""
""""
Created on Sun Oct 20 11:35:23 2019
class that opens a shell when ssh into device to call commands 
@author: hmkumba
channel class created using code from https://evilttl.com/wiki/Execute-MULTIPLE-commands-with-Python
"""

import paramiko
from paramiko import client
import cmd
import time
import sys

class channel:

    chan = None
    ssh = None

    def __init__(self, address, username, password,port='22'):
        #create client
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #ssh into device
        self.ssh.connect(address, username=username, password=password,look_for_keys=False,port=port)
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #invoke a shell
        self.chan = self.ssh.invoke_shell()

        self.chan.send('terminal length 0\n')
        time.sleep(1)

    #method for sending commands to shell
    def sendCommand(self, command):
        #send the command
        self.chan.send(command)
        self.chan.send('\n')
        time.sleep(5)
        response = self.chan.recv(9999)
        output = response.decode('ascii').split(',')
        #change bytes to string format
        output = ''.join(output)
        return output

    #method for closing the ssh session
    def closeSession(self):
        self.ssh.close()


class ssh:

    client = None

    def __init__(self, address, username, password,port='22'):
        self.address = address
        self.username = username
        self.client = client.SSHClient()
        self.client.set_missing_host_key_policy(client.AutoAddPolicy())
        self.client.connect(address, username = username, password=password, look_for_keys=False,port=port)

    def sendCommand(self, command):
        if(self.client):
            stdin, stdout, stderr = self.client.exec_command(command)
            while not stdout.channel.exit_status_ready():
                # Print data when available
                if stdout.channel.recv_ready():
                    alldata = stdout.readline()
                    prevdata = b"1"
                    while prevdata:
                        prevdata = stdout.readline()
                        alldata += prevdata
                    # return alldata to calling function
                    return alldata
        else:
            # return None if connection fails to open
            return 'failed to execute commnand because the ssh connection failed to open'

    def exit_ssh(self):
        self.client.close()