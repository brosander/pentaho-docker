#!/usr/bin/python

import pexpect, argparse, kadmin, ktutil
from subprocess import check_output

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='''
  This script create a new mongo user with kerberos principal
  ''')
  parser.add_argument('-n', '--principalName', default=None, help='Principal name')
  parser.add_argument('-d', '--database', default='test', help='Mongo Db')
  parser.add_argument('-r', '--roles', default='read', help='Comma separated list of roles')
  parser.add_argument('-p', '--password', default=None, help='Password')
  parser.add_argument('-k', '--keytab', default=None, help='Keytab name (optional)')
  args = parser.parse_args()
  domain = str(check_output("grep default_realm /etc/krb5.conf | awk '{print $NF}'", shell=True)).strip()
  roles = ','.join([ '"' + role + '"' for role in args.roles.split(',') ])
  kadmin.kadmin('addprinc ' + args.principalName, args.password)
  print str(check_output(['/mongodb/bin/mongo', '--eval', 'db = db.getSiblingDB("' + args.database + '"); db.system.users.remove( { user: "' + args.principalName + '@' + domain + '" } ); db.addUser( { "user": "' + args.principalName + '@' + domain + '", "roles": [' + roles + '], "userSource": "$external" } )']))
  if args.keytab is not None:
    ktutil.ktutil(['addent -password -p ' + args.principalName + '@' + domain + ' -k 1 -e aes256-cts', 'wkt ' + args.keytab], [args.password])
