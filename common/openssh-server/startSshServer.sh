#!/bin/bash
python /root/setPassword.py -u root -p password -f /etc/shadow -i
/usr/sbin/sshd -D
