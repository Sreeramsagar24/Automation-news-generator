# ssh.py
import paramiko
import os
from datetime import datetime
import json
import requests

def open_json():
    with open('C:\\Users\\SRIRAM\\PycharmProjects\\pythondeveloper\\AUTOMATION_PROJECT\\config\\config.json','r') as f:
        return json.load(f)

def ssh_connection():
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

    except Exception as e:
        print(f" Failed to connect: {e}")

ssh_connection()




