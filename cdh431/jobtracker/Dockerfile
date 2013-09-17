from docker:5000/cdh431base
run apt-get install -y hadoop-0.20-mapreduce-jobtracker
run /root/updateCore.sh
run /root/updateHdfs.sh
run mkdir /var/local/hadoop
run chown mapred:mapred /var/local/hadoop
add jobtracker_init.sh /root/
run chmod +x /root/jobtracker_init.sh
