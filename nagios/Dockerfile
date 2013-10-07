from ubuntu
run echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
env DEBIAN_FRONTEND noninteractive
run apt-get update
run apt-get install -y nagios3 nsca net-tools openssh-server python2.7
run mkdir /var/run/sshd
run chmod 0755 /var/run/sshd
run sed -i 's/check_external_commands=0/check_external_commands=1/g' /etc/nagios3/nagios.cfg
add https://raw.github.com/brosander/pentaho-docker/master/common/openssh-server/setPassword.py /root/
add https://gist.github.com/brosander/6870106/raw/a060fb65f453e82cf28e5232b508a037b569fb32/startNagios.sh /root/
run chmod 0755 /root/startNagios.sh
run python /root/setPassword.py -i -u root -p password
CMD ["/root/startNagios.sh"]
