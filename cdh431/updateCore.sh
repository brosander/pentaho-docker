#!/bin/bash
python /root/hadoopProperties.py -i -f /etc/hadoop/conf/core-site.xml -p fs.defaultFS -v hdfs://$NAMENODE:9000/
