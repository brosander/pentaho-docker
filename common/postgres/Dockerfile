from bryan-ubuntu:5000/openssh-server
run apt-get install -y postgresql
run python /root/setPassword.py -i -u root -p password
run python /root/setPassword.py -i -u postgres -p password
add pgStartup.sh /root/
add preparePostgres.sql /etc/
run chmod a+r /etc/preparePostgres.sql
run chmod +x /root/pgStartup.sh
run sed -i.bak 's/#\(listen_addresses\s*=.*\)localhost/\1\*/g' /etc/postgresql/9.1/main/postgresql.conf
run sed -i.bak 's/\(local\s*all\s*all\s*\)peer/\1md5/g' /etc/postgresql/9.1/main/pg_hba.conf
run sed -i 's/127.0.0.1\/32/172.17.0.0\/16/g' /etc/postgresql/9.1/main/pg_hba.conf
EXPOSE 5432:5432
ENTRYPOINT ["/root/pgStartup.sh"]
