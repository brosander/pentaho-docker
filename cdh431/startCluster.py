#!/usr/bin/python

import argparse
import paramiko
import socket
from subprocess import Popen, PIPE
import sys
import time

jobtracker = 'dummyJobtrackerHostname'
namenode = 'dummyNamenodeHostname'


def startContainer(hostname, imageName, startCommand):
  cmd = ['docker', 'run']
  cmd.extend(['-e', 'JOBTRACKER=' + jobtracker])
  cmd.extend(['-e', 'NAMENODE=' + namenode])
  cmd.extend(['-d'])
  cmd.extend(['-h', hostname])
  cmd.extend([imageName])
  cmd.extend([startCommand])
  print 'Starting ' + hostname + ' with image ' + imageName
  Popen(cmd, stdout=PIPE) 


def connectSsh(hostname, username = 'root', password = 'password'):
  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  ssh.connect(hostname, username=username, password=password)
  return ssh

def runCommands(commands, hostname, username = 'root', password = 'password'):
  ssh = connectSsh(hostname, username, password)
  result = []
  for command in commands:
    print 'Running: ' + command + ' on host ' + hostname
    stdin, stdout, stderr = ssh.exec_command(command) 
    result.append((stdout.readlines(), stderr.readlines()))
  return result

def waitOnSsh(hostname, username = 'root', password = 'password'):
  ssh = None
  while ssh is None:
    try:
      ssh = connectSsh(hostname, username, password)
      ssh.close()
      print hostname + ' ssh server up'
      return
    except socket.error:
      time.sleep(1)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='''
  This script is designed start a cdh431 hadoop cluster
  ''')
  parser.add_argument('-d', '--domain', default='hadoop', help='Domain suffix for all hostnames')
  parser.add_argument('-j', '--jobtracker', default='jobtracker', help='Jobtracker hostname')
  parser.add_argument('-n', '--namenode', default='namenode', help='Namenode hostname')
  args = parser.parse_args()
  jobtracker = args.jobtracker + '.' + args.domain
  namenode = args.namenode + '.' + args.domain
  datanodes = ['datanode' + str(num) + '.' + args.domain for num in range(2)]
  startContainer(namenode, 'docker:5000/cdh431namenode', '/root/namenode_init.sh')
  startContainer(jobtracker, 'docker:5000/cdh431jobtracker', '/root/jobtracker_init.sh')
  waitOnSsh(namenode)
  for datanode in datanodes:
    startContainer(datanode, 'docker:5000/cdh431datanode', '/root/datanode_init.sh')
  for datanode in datanodes:
    waitOnSsh(datanode)
  runCommands([
      'su - hdfs -c "hadoop fs -mkdir /tmp"', 
      'su - hdfs -c "hadoop fs -chmod -R 1777 /tmp"',
      'su - hdfs -c "hadoop fs -mkdir -p /var/lib/hadoop-hdfs/cache/mapred/mapred/staging"',
      'su - hdfs -c "hadoop fs -chmod 1777 /var/lib/hadoop-hdfs/cache/mapred/mapred/staging"',
      'su - hdfs -c "hadoop fs -chown -R mapred /var/lib/hadoop-hdfs/cache/mapred"',
      'su - hdfs -c "hadoop fs -mkdir /tmp/mapred/system"',
      'su - hdfs -c "hadoop fs -chown mapred:hadoop /tmp/mapred/system"'
    ], namenode)
  runCommands(['service hadoop-0.20-mapreduce-jobtracker start'], jobtracker)
  for datanode in datanodes:
    runCommands(['service hadoop-0.20-mapreduce-tasktracker start'], datanode)
