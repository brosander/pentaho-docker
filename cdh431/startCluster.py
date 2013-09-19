#!/usr/bin/python

import argparse
import os
import paramiko
import shutil
import socket
from subprocess import Popen, PIPE
import sys
import time

jobtracker = 'dummyJobtrackerHostname'
namenode = 'dummyNamenodeHostname'

def createHostDisk(hostname, gigabytes):
  path = os.path.expanduser('~/docker-directories/' + hostname)
  imageName = path + '/partition.ext3'
  folderPath = path + '/mnt'
  if os.path.exists(path):
    print 'Removing existing path: ' + path
    Popen(['sudo', 'umount', folderPath], stdout=PIPE).communicate()
    shutil.rmtree(path)
  os.makedirs(folderPath)
  cmd = ['dd', 'if=/dev/zero', 'of=' + imageName,'bs=1G', 'count=' + str(gigabytes)]
  print 'Running: ' + ' '.join(cmd)
  Popen(cmd, stdout = PIPE).communicate()
  cmd = ['mkfs.ext3', '-F', imageName]
  print 'Running: ' + ' '.join(cmd)
  Popen(cmd, stdout = PIPE).communicate()
  cmd = ['sudo', 'mount', '-o', 'loop,rw', imageName, folderPath]
  print 'Running: ' + ' '.join(cmd)
  Popen(cmd, stdout = PIPE).communicate()
  return folderPath

def startContainer(hostname, imageName, startCommand, docker_extra_args = []):
  cmd = ['docker', 'run']
  cmd.extend(['-e', 'JOBTRACKER=' + jobtracker])
  cmd.extend(['-e', 'NAMENODE=' + namenode])
  cmd.extend(['-d'])
  cmd.extend(['-h', hostname])
  cmd.extend(docker_extra_args)
  cmd.extend([imageName])
  cmd.extend([startCommand])
  print 'Starting ' + hostname + ' with image ' + imageName
  print 'Command: ' + ' '.join(cmd)
  Popen(cmd, stdout=PIPE) 

class SshCredentials:
  def __init__(self, hostname, username = 'root', password = 'password'):
    self.hostname = hostname
    self.username = username
    self.password = password

def connectSsh(credentials):
  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  ssh.connect(credentials.hostname, username=credentials.username, password=credentials.password)
  return ssh

def runCommands(commands, credentials):
  ssh = connectSsh(credentials)
  result = []
  for command in commands:
    print 'Running: ' + command + ' on host ' + credentials.hostname
    stdin, stdout, stderr = ssh.exec_command(command) 
    stdin.close()
    stdin.channel.shutdown_write()
    result.append((stdout.readlines(), stderr.readlines()))
  ssh.close()
  return result

def waitOnSsh(credentials):
  ssh = None
  while ssh is None:
    try:
      ssh = connectSsh(credentials)
      ssh.close()
      print credentials.hostname + ' ssh server up'
      return
    except socket.error:
      time.sleep(1)

def writeFileOverSsh(credentials, file_string, remote_path):
  ssh = connectSsh(credentials)
  print "Writing " + remote_path + " to " + credentials.hostname
  stdin, stdout, stderr = ssh.exec_command('cat > ' + remote_path)
  stdin.write(file_string)
  stdin.flush()
  stdin.close()
  stdin.channel.shutdown_write()
  result = (stdout.read().splitlines(), stderr.read().splitlines())
  ssh.close()
  return result

def createAndPushZookeeperConfig(credential_list):
  config = ['tickTime=2000']
  config.append('dataDir=/var/lib/zookeeper')
  config.append('clientPort=2181')
  config.append('initLimit=10')
  config.append('syncLimit=5')
  for credentials, index in zip(credential_list, range(1, len(credential_list) + 1)):
    config.append(''.join(['server.', str(index), '=', credentials.hostname, ':2888:3888']))
  config_str = '\n'.join(config)
  for credentials in credential_list:
    writeFileOverSsh(credentials, config_str, '/root/zookeeper.config')

def configureZookeeper(credential_list):
  createAndPushZookeeperConfig(credential_list)
  for credentials, index in zip(credential_list, range(1, len(credential_list) + 1)):
    print str(runCommands([
        'echo "export JAVA_HOME=/usr/lib/jvm/`ls /usr/lib/jvm/ | sort | tail -n 1`" >> /etc/default/bigtop-utils',
        'cp /root/zookeeper.config /etc/zookeeper/conf/zoo.cfg',
        'service zookeeper-server init --force --myid=' + str(index),
        'service zookeeper-server start'
      ], credentials))

def configureHBase(credential_list, namenode_credentials, zookeeper_hostnames):
  zookeeper_quorum = ','.join(zookeeper_hostnames)
  print str(runCommands([
      'su - hdfs -c "hadoop fs -mkdir /hbase"',
      'su - hdfs -c "hadoop fs -chown hbase /hbase"'
    ], namenode_credentials))
  common_commands = [
      'echo "export HBASE_MANAGES_ZK=false" > /etc/hbase/conf/hbase-env.sh',
      'python hadoopProperties.py -i -f /etc/hbase/conf/hbase-site.xml -p hbase.cluster.distributed -v true',
      'python hadoopProperties.py -i -f /etc/hbase/conf/hbase-site.xml -p hbase.rootdir -v hdfs://' + namenode + ':9000/hbase',
      'python hadoopProperties.py -i -f /etc/hbase/conf/hbase-site.xml -p hbase.zookeeper.quorum -v ' + zookeeper_quorum,
      'python hadoopProperties.py -i -f /etc/hbase/conf/hbase-site.xml -p hbase.zookeeper.property.clientPort -v 2181',
      ]
  #Setup hbase master
  master_commands = []
  master_commands.extend(common_commands)
  master_commands.extend([
      'python hadoopProperties.py -i -f /etc/hbase/conf/hbase-site.xml -p hbase.rest.port -v 60050',
      'service hbase-master start',
      'service hbase-rest start',
      'service hbase-thrift start'
    ])
  print str(runCommands(master_commands, credential_list[0]))
  #Setupd region servers
  region_commands = []
  region_commands.extend(common_commands)
  region_commands.append('service hbase-regionserver start')
  for credentials in credential_list[1:]:
    print str(runCommands(region_commands, credentials))

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='''
  This script is designed start a cdh431 hadoop cluster
  ''')
  parser.add_argument('-d', '--domain', default='hadoop', help='Domain suffix for all hostnames')
  parser.add_argument('-j', '--jobtracker', default='jobtracker', help='Jobtracker hostname')
  parser.add_argument('-n', '--namenode', default='namenode', help='Namenode hostname')
  parser.add_argument('-u', '--users', default='bryan', help='Comma seperated list of users')
  parser.add_argument('-o', '--datanodes', default=2, type=int, help='Number of datanodes to create')
  parser.add_argument('-s', '--size', default=1, type=int, help='Size (GB) of datanode disks')
  parser.add_argument('-z', '--zookeeper_size', default=3, type=int, help='The number of nodes in the zookeeper quorum')
  parser.add_argument('-b', '--hbase_size', default=3, type=int, help='The number of nodes to use for hbase')
  args = parser.parse_args()
  jobtracker = args.jobtracker + '.' + args.domain
  namenode = args.namenode + '.' + args.domain
  datanodes = ['datanode' + str(num) + '.' + args.domain for num in range(args.datanodes)]
  all_nodes = [jobtracker, namenode]
  all_nodes.extend(datanodes)
  zookeeper_nodes = all_nodes[:args.zookeeper_size]
  hbase_nodes = all_nodes[:args.zookeeper_size]
  startContainer(namenode, 'docker:5000/cdh431namenode', '/root/namenode_init.sh')
  startContainer(jobtracker, 'docker:5000/cdh431jobtracker', '/root/jobtracker_init.sh')
  folders = {}
  for datanode in datanodes:
    folders[datanode] = createHostDisk(datanode, args.size)
  waitOnSsh(SshCredentials(namenode))
  for datanode in datanodes:
    folder = folders[datanode]
    dn = folder + '/dn'
    os.makedirs(dn)
    local = folder + '/local'
    os.makedirs(local)
    startContainer(datanode, 'docker:5000/cdh431datanode', '/root/datanode_init.sh', 
      ['-v', dn + ':/data/1/dfs/dn', '-v', local + ':/data/1/mapred/local'])
  for datanode in datanodes:
    waitOnSsh(SshCredentials(datanode))
  runCommands([
      'su - hdfs -c "hadoop fs -mkdir /tmp"', 
      'su - hdfs -c "hadoop fs -chmod -R 1777 /tmp"',
      'su - hdfs -c "hadoop fs -mkdir -p /var/lib/hadoop-hdfs/cache/mapred/mapred/staging"',
      'su - hdfs -c "hadoop fs -chmod 1777 /var/lib/hadoop-hdfs/cache/mapred/mapred/staging"',
      'su - hdfs -c "hadoop fs -chown -R mapred /var/lib/hadoop-hdfs/cache/mapred"',
      'su - hdfs -c "hadoop fs -mkdir /tmp/mapred/system"',
      'su - hdfs -c "hadoop fs -chown mapred:hadoop /tmp/mapred/system"'
    ], SshCredentials(namenode))
  runCommands(['service hadoop-0.20-mapreduce-jobtracker start'], SshCredentials(jobtracker))
  for datanode in datanodes:
    runCommands(['service hadoop-0.20-mapreduce-tasktracker start'], SshCredentials(datanode))
  for user in args.users.split(','):
    runCommands([
        'su - hdfs -c "hadoop fs -mkdir /user/' + user + '"',
        'su - hdfs -c "hadoop fs -chown ' + user + ' /user/' + user + '"'
      ], SshCredentials(namenode))
  configureZookeeper([SshCredentials(hostname) for hostname in zookeeper_nodes])
  configureHBase([SshCredentials(hostname) for hostname in hbase_nodes], SshCredentials(namenode), zookeeper_nodes)
