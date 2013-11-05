#!/bin/bash
/usr/sbin/mysqld &
until echo "GRANT ALL ON *.* TO admin@'%' IDENTIFIED BY 'password' WITH GRANT OPTION; FLUSH PRIVILEGES" | mysql --password=password
do
  echo "Waiting for mysql to come up."
  sleep 1
done
/usr/sbin/sshd -D
