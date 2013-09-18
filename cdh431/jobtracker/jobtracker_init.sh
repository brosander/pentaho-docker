#!/bin/bash
/root/updateCore.sh
/root/updateHdfs.sh
/root/updateMapred.sh
service hadoop-0.20-mapreduce-jobtracker start
/usr/sbin/sshd -D
