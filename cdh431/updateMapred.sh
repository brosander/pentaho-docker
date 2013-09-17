#!/bin/bash
python /root/hadoopProperties.py -i -f /etc/hadoop/conf/mapred-site.xml -p mapred.job.tracker -v hdfs://$JOBTRACKER:8021/
