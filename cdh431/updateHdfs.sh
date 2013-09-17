#!/bin/bash
python /root/hadoopProperties.py -i -f /etc/hadoop/conf/hdfs-site.xml -p dfs.permissions.superusergroup -v hadoop
