#!/bin/bash
rm /var/lib/krb5kdc/* || true
rm /etc/krb5kdc/* || true
rm /home/mongodb/mongod.keytab || true
HOSTNAME="`hostname`"
DEFAULT_REALM_DOMAIN="`hostname -f | sed \"s/$HOSTNAME\.//g\"`"
DEFAULT_REALM="`echo $DEFAULT_REALM_DOMAIN | sed 's/\(.*\)/\U\1/g'`"
sed "s/DEFAULT_REALM_DOMAIN/$DEFAULT_REALM_DOMAIN/g" /root/krb5.conf | sed "s/DEFAULT_REALM/$DEFAULT_REALM/g" | sed "s/KDC_NAME/$HOSTNAME/g" | sed "s/ADMIN_SERVER_NAME/$HOSTNAME/g" > /etc/krb5.conf
python /root/newrealm.py
sed "s/DEFAULT_REALM/$DEFAULT_REALM/g" /root/kadm5.acl > /etc/krb5kdc/kadm5.acl
python /root/kadmin.py -c "addprinc admin" -p password
python /root/kadmin.py -c "addprinc mongodb/`hostname -f`" -p password
python /root/ktutil.py -c "addent -password -p mongodb/`hostname -f`@$DEFAULT_REALM -k 1 -e aes256-cts; wkt /home/mongodb/mongod.keytab" -p password
chown mongodb:mongodb /home/mongodb/mongod.keytab
chmod 600 /home/mongodb/mongod.keytab
su - mongodb -c "export KRB5_KTNAME=/home/mongodb/mongod.keytab && /mongodb/bin/mongod --config /home/mongodb/mongod.conf"
python /root/createUser.py -n kettle/kettle -p password -k test.keytab -d test -r readWrite
/usr/sbin/sshd -D
