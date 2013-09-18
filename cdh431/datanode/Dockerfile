from docker:5000/cdh431base
run apt-get install -y hadoop-0.20-mapreduce-tasktracker hadoop-hdfs-datanode
run echo python /root/hadoopProperties.py -i -f /etc/hadoop/conf/hdfs-site.xml -p dfs.datanode.data.dir -v /data/1/dfs/dn >> /root/updateHdfs.sh
run echo python /root/hadoopProperties.py -i -f /etc/hadoop/conf/mapred-site.xml -p mapred.local.dir -v /data/1/mapred/local >> /root/updateMapred.sh
run mkdir -p /data/1/dfs/dn
run chown hdfs:hdfs /data/1/dfs/dn
run mkdir -p /data/1/mapred/local
run chown mapred:hadoop /data/1/mapred/local
run mkdir /var/local/hadoop
run chown hdfs:hadoop /var/local/hadoop
add datanode_init.sh /root/
run chmod +x /root/datanode_init.sh
