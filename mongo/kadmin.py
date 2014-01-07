#!/usr/bin/python

import pexpect, argparse

def kadmin(command, password):
  child = pexpect.spawn('kadmin.local')
  child.expect_exact("kadmin.local:")
  child.sendline(command)
  child.expect_exact(command)
  if password is not None:
    child.expect("Enter password .*:")
    child.sendline(password)
    if child.expect(["Re-enter password .*:", "kadmin.local:"]) == 0:
      child.sendline(password)
  else:
    child.expect_exact("kadmin.local:")
  print str(child.before).strip()
  child.sendline("quit")
  child.expect(pexpect.EOF)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='''
  This script will run the specified kadmin.local command
  ''')
  parser.add_argument('-c', '--command', default=None, help='Command to run')
  parser.add_argument('-p', '--password', default= None, help='Password to enter at the prompt')
  args = parser.parse_args()
  kadmin(args.command, args.password)
