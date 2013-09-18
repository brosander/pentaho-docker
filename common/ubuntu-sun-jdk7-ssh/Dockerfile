from docker:5000/openssh-server
add jdk-7u40-linux-x64.tar.gz /usr/lib/jvm/
run tar -C /usr/lib/jvm -zxf /usr/lib/jvm/jdk-7u40-linux-x64.tar.gz
run rm /usr/lib/jvm/jdk-7u40-linux-x64.tar.gz
env JAVA_HOME /usr/lib/jvm/jdk1.7.0_40
env PATH /usr/lib/jvm/jdk1.7.0_40/bin:$PATH
