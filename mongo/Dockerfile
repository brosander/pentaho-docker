from bryan-ubuntu:5000/openssh-server
run echo "deb http://archive.ubuntu.com/ubuntu precise main universe multiverse" > /etc/apt/sources.list
run apt-get update
run apt-get install -y libssl0.9.8 snmp snmpd cyrus-sasl2-dbg cyrus-sasl2-mit-dbg libsasl2-2 libsasl2-dev libsasl2-modules libsasl2-modules-gssapi-mit krb5-kdc krb5-admin-server expect python python-pexpect
run wget -O - http://downloads.10gen.com/linux/mongodb-linux-x86_64-subscription-ubuntu1204-2.4.8.tgz | tar -zxf -
run ln -s /mongodb-linux-x86_64-subscription-ubuntu1204-2.4.8/ /mongodb
run mkdir -p /data/db
run adduser --disabled-password --gecos "" mongodb
run chown mongodb /data/db
run touch /var/log/mongod.log
run chown mongodb /var/log/mongod.log
add krb5.conf /root/
add kadm5.acl /root/
add newrealm.py /root/
add mongoStart.sh /root/
add kadmin.py /root/
add ktutil.py /root/
add createUser.py /root/
add mongod.conf /home/mongodb/
run chown mongodb:mongodb /home/mongodb/mongod.conf
run chmod +x /root/mongoStart.sh
run python /root/setPassword.py -u root -p password -f /etc/shadow -i
entrypoint ["/root/mongoStart.sh"]
