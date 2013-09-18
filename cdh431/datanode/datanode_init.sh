#!/bin/bash
/root/updateCore.sh
/root/updateHdfs.sh
/root/updateMapred.sh
chown -R hdfs:hdfs /data/1/dfs/dn
chown -R mapred:hadoop /data/1/mapred/local
service hadoop-hdfs-datanode start
/usr/sbin/sshd -D
