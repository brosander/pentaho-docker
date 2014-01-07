#!/bin/bash
python /root/configDns.py -g -i "`ifconfig eth0 | grep "inet addr" | awk '{print $2}' | sed 's/.*://g'`"
service bind9 restart
