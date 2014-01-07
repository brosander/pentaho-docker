#!/usr/bin/python

import pexpect, argparse

def ktutil(commands, passwords):
  child = pexpect.spawn('ktutil')
  child.expect_exact("ktutil:")
  for cmd in commands:
    child.sendline(cmd)
    if child.expect(["Password for .*:", "ktutil:"]) == 0:
      print str(child.before).strip()
      child.sendline(passwords.pop(0))
      child.expect_exact("ktutil:")
    print str(child.before).strip()
  child.sendline("quit")
  child.expect(pexpect.EOF)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='''
  This script will run the specified ktutil commands
  ''')
  parser.add_argument('-c', '--commands', default=None, help='Commands to run')
  parser.add_argument('-p', '--passwords', default= None, help='Password to enter at the prompt')
  args = parser.parse_args()
  commands = args.commands.split(';')
  passwords = args.passwords.split(';')
  ktutil(commands, passwords)
