#!/bin/bash
python /root/hadoopProperties.py -i -f /etc/hadoop/conf/hdfs-site.xml -p dfs.permissions.superusergroup -v hadoop
python /root/hadoopProperties.py -i -f /etc/hadoop/conf/hdfs-site.xml -p dfs.datanode.max.xciever -v 4096
python /root/hadoopProperties.py -i -f /etc/hadoop/conf/hdfs-site.xml -p dfs.permissions -v false
