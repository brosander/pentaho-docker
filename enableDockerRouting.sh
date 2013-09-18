#!/bin/bash
sudo su - root -c "echo 1 > /proc/sys/net/ipv4/ip_forward"
sudo /sbin/iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo /sbin/iptables -A FORWARD -i eth0 -o docker0 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo /sbin/iptables -A FORWARD -i docker0 -o eth0 -j ACCEPT
