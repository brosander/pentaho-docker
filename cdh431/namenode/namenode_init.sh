#$!/bin/bash
/root/updateCore.sh
/root/updateHdfs.sh
/root/updateMapred.sh
su -s /bin/bash hdfs -c "hadoop namenode -format"
service hadoop-hdfs-namenode start
