from docker:5000/cdh431base
run apt-get install -y hadoop-hdfs-namenode
run echo python /root/hadoopProperties.py -i -f /etc/hadoop/conf/hdfs-site.xml -p dfs.namenode.name.dir -v /data/1/dfs/nn >> /root/updateHdfs.sh
run mkdir -p /data/1/dfs/nn
run chown hdfs:hdfs /data/1/dfs/nn
run mkdir /var/local/hadoop
run chown hdfs:hdfs /var/local/hadoop
add namenode_init.sh /root/
run chmod +x /root/namenode_init.sh
