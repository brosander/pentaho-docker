from docker:5000/ubuntu-sun-jdk7-ssh
run apt-get install -y curl
run echo deb [arch=amd64] http://archive.cloudera.com/cdh4/ubuntu/precise/amd64/cdh precise-cdh4.3.1 contrib > /etc/apt/sources.list.d/cloudera.list
run echo deb-src http://archive.cloudera.com/cdh4/ubuntu/precise/amd64/cdh precise-cdh4.3.1 contrib >> /etc/apt/sources.list.d/cloudera.list
run curl -s http://archive.cloudera.com/cdh4/ubuntu/precise/amd64/cdh/archive.key | apt-key add -
run apt-get update
run apt-get install -y bigtop-jsvc bigtop-utils hadoop hadoop-hdfs netcat-openbsd psmisc zookeeper python-lxml zookeeper-server hbase-master hbase-rest hbase-thrift hbase-regionserver
run python /root/setPassword.py -i -u root -p password
run cp /etc/hadoop/conf/core-site.xml /etc/hadoop/conf/mapred-site.xml
mkdir /root/.ssh
add hadoop-env.sh /etc/hadoop/conf.empty/
run echo export JAVA_HOME=$JAVA_HOME >> /etc/hadoop/conf/hadoop-env.sh
add hadoopProperties.py /root/
add updateCore.sh /root/
run chmod +x /root/updateCore.sh
add updateHdfs.sh /root/
run chmod +x /root/updateHdfs.sh
add updateMapred.sh /root/
run chmod +x /root/updateMapred.sh
