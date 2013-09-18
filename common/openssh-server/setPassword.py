#!/usr/bin/python

import argparse
import os
from subprocess import Popen, PIPE
import sys

def getHashedPassword(password):
  p1 = Popen(['openssl', 'passwd', '-1', password], stdout = PIPE)
  return p1.communicate()[0].decode('UTF-8').strip()

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='''
  This script will set the user's password
  ''')
  parser.add_argument('-f', '--filename', default='/etc/shadow', help='Filename to edit')
  parser.add_argument('-u', '--username', help='Username for password change', required=True)
  parser.add_argument('-p', '--password', help='New password', required=True)
  parser.add_argument('-i', '--inplace', action='store_true', help='Edit the file in place')
  args = parser.parse_args()
  with file(args.filename) as f:
    lines = f.readlines()
  for line, index in zip(lines, range(len(lines))):
    splitLine = line.split(':')
    if splitLine[0] == args.username:
      splitLine[1] = getHashedPassword(args.password)
      lines[index] = ':'.join(splitLine)
  if args.inplace:
    with open(args.filename, 'w') as f:
      for line in lines:
        f.write(line)
  else:
    for line in lines:
      print line.strip()
