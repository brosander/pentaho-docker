#!/usr/bin/python

import pexpect
child = pexpect.spawn('krb5_newrealm')
child.expect("Enter KDC database master key:")
child.sendline("password")
child.expect("Re-enter KDC database master key to verify:")
child.sendline("password")
child.expect(pexpect.EOF)
