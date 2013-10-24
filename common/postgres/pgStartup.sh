#!/bin/bash
service postgresql start
if [ ! -e /etc/postgresql/9.1/main/pg_setup_output ]; then
  until su - postgres -c "psql -f /etc/preparePostgres.sql > /etc/postgresql/9.1/main/pg_setup_output"
  do
    echo "Waiting for postgres to come up."
    sleep 1
  done
  sed -i 's/\(local\s*all\s*\postgres\s*\)peer/\1md5/g' /etc/postgresql/9.1/main/pg_hba.conf
  service postgresql restart
fi
/usr/sbin/sshd -D
