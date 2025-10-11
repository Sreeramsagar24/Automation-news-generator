# ssh.py
"""
Module to create SSH connections using Paramiko
"""
import json
import paramiko
from paramiko.ssh_exception import SSHException

def open_json():
    """
    :return: it opens the json file
    """
    with open('C:\\Users\\SRIRAM\\PycharmProjects\\pythondeveloper\\'
              'AUTOMATION_PROJECT\\config\\config.json','r',encoding="utf-8") as f:
        return json.load(f)

def ssh_connection():
    """
    it makes the ssh connection
    """
    details=open_json()
    ssh_cfg =details["ssh"]
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            ssh_cfg["host"],
            port=ssh_cfg["port"],
            username=ssh_cfg["username"],
            password=ssh_cfg["password"]
        )
        print("SSH connection established successfully ")
        return ssh

    except SSHException as e:
        print(f" Failed to connect: {e}")
        return None
ssh_connection()
