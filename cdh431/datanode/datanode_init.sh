#$!/bin/bash
/root/updateCore.sh
/root/updateHdfs.sh
/root/updateMapred.sh
service hadoop-hdfs-datanode start
