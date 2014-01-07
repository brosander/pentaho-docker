from bryan-ubuntu:5000/openssh-server
run apt-get update
run apt-get install -y bind9 bind9utils dnsutils python
add dnsStart.sh /root/
add refresh.sh /root/
add configDns.py /root/
run chmod +x /root/dnsStart.sh
run chmod +x /root/refresh.sh
run python /root/configDns.py -p -a -n forwarders -v "{ 8.8.8.8; 4.4.4.4; }" -w /root/.configDns
run python /root/configDns.py -p -a -n directory -v '"/var/cache/bind"' -w /root/.configDns
run python /root/configDns.py -p -a -n dnssec-validation -v auto -w /root/.configDns
run python /root/configDns.py -p -a -n auth-nxdomain -v no -w /root/.configDns
run python /root/configDns.py -p -a -n listen-on-v6 -v "{ any; }" -w /root/.configDns
run python /root/setPassword.py -u root -p password -f /etc/shadow -i
EXPOSE 53:53
ENTRYPOINT ["/root/dnsStart.sh"]
