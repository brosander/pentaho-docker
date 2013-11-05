from bryan-ubuntu:5000/openssh-server
run echo mysql-server mysql-server/root_password password password | debconf-set-selections
run echo mysql-server mysql-server/root_password_again password password | debconf-set-selections
run apt-get install -y mysql-server
run python /root/setPassword.py -i -u root -p password
run sed -i 's/^bind-address/# bind-address/g' /etc/mysql/my.cnf
add mysqlStartup.sh /root/
run chmod +x /root/mysqlStartup.sh
EXPOSE 3306:3306
ENTRYPOINT ["/root/mysqlStartup.sh"]
