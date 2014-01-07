#!/usr/bin/python

import argparse
import ast
from os.path import expanduser

def remove_host(old_config, qualified_hostname, hosts):
  if qualified_hostname in hosts:
    address = hosts[qualified_hostname].split('.')
    for i in range(len(address)):
      octets = address[:i+1]
      octets.reverse()
      arpa = '.'.join(octets) + '.in-addr.arpa'
      if arpa in old_config['domains']:
        domain = old_config['domains'][arpa]
        if qualified_hostname in domain['hosts']:
          del domain['hosts'][qualified_hostname]
    del hosts[qualified_hostname]

def add_host(old_config, qualified_hostname, ip, hosts, octets):
  remove_host(old_config, qualified_hostname, hosts)
  hosts[qualified_hostname] = ip
  network = ip.split('.')[:octets]
  network.reverse()
  network = '.'.join(network)
  host = ip.split('.')[octets:]
  host.reverse()
  host = '.'.join(host)
  arpa = network + '.in-addr.arpa'
  if not arpa in old_config['domains']:
    old_config['domains'][arpa] = {'hosts': {}}
  old_config['domains'][arpa]['hosts'][qualified_hostname] = host
  
def save_config(old_config, workingFile):
  with open(workingFile, 'w') as f:
    f.write(str(old_config) + '\n')

def print_details(old_config):
  print str(old_config)

def generate_output(old_config, folder, ip_address):
  with open(folder + '/named.conf.options', 'w') as f:
    f.write('options {\n')
    for k, v in old_config['options'].items():
      f.write('  ' + k + ' ' + v + ';\n')
    f.write('};\n')
  with open(folder + '/named.conf.local', 'w') as f:
    for domain_name, domain in old_config['domains'].items():
      f.write('zone "' + domain_name + '" {\n')
      f.write('  type master;\n')
      f.write('  notify no;\n')
      filename = domain_name
      if domain_name.endswith('.in-addr.arpa'):
        filename = domain_name[:domain_name.find('.in-addr.arpa')]
        ns_ip = ip_address.split('.')[len(filename.split('.')):]
        ns_ip.reverse()
        ns_ip = '.'.join(ns_ip)
        if len(domain['hosts']) == 0:
          continue
        ns = 'ns.' + '.'.join(domain['hosts'].iterkeys().next().split('.')[1:])
        domain['hosts'][ns] = ns_ip
      else:
        ns = 'ns.' + domain_name
        domain['hosts'][ns] = ip_address
      filename = "db." + filename
      f.write('  file "' + folder + '/' + filename + '";\n')
      f.write('};\n')
      serial = 1
      try:
        with open(folder + '/' + filename) as db:
          for line in db.readlines():
            if 'Serial' in line:
              serial = int(line.strip().split()[0]) + 1
      except IOError:
        pass
      with open(folder + '/' + filename, 'w') as db:
        db.write('$TTL  604800\n')
        db.write('@ IN  SOA ' + ns + '. ' + ns + '. (\n')
        db.write('            ' + str(serial) + '   ; Serial\n')
        db.write('       604800   ; Refresh\n')
        db.write('        86400   ; Retry\n')
        db.write('      2419200   ; Expire\n')
        db.write('       604800 ) ; Negative Cache TTL\n')
        db.write(';\n')
        db.write('@ IN  NS  ' + ns + '.\n')
        middle_str = ' IN  A '
        end_str = ''
        if domain_name.endswith('.in-addr.arpa'):
          for hostname, ip in domain['hosts'].items():
            db.write(ip + ' IN  PTR ' + hostname  + '.\n')
        else:
          for hostname, ip in domain['hosts'].items():
            db.write(hostname.split('.')[0] + ' IN  A ' + ip + '\n')

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='''
  This script is used to generate and update a bind9 server config
  ''', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("-f", "--folder", default="/etc/bind", help="Bind9 directory")
  parser.add_argument("-d", "--domain", default=None, help="Domain")
  parser.add_argument("-p", "--options", action="store_true", help="Bind9 options")
  parser.add_argument("-r", "--remove", action="store_true", help="Remove domain")
  parser.add_argument("-a", "--add", action="store_true", help="Add entry")
  parser.add_argument("-n", "--name", default=None, help="Hostname to add")
  parser.add_argument("-i", "--ip", default=None, help="Ip to add")
  parser.add_argument("-o", "--octets", default=2, type=int, help="The number of octets in the netmask")
  parser.add_argument("-g", "--generate", action="store_true", help="Output config")
  parser.add_argument("-t", "--temporary", action="store_true", help="Don't save changes, just write to stdout")
  parser.add_argument("-v", "--value", default=None, help="Value for option")
  parser.add_argument("-w", "--workingFile", default=expanduser('~/.configDns'), help="File to use")
  args = parser.parse_args()
  try:
    with open(args.workingFile) as config:
      old_config = ast.literal_eval(''.join(config.readlines()))
  except IOError:
    old_config = { 'domains' : {}, 'options' : {}}
  if args.domain:
    if args.options:
      raise Exception("Can specify domain (-d) or options (-p) but not both")
    if args.domain in old_config['domains']:
      domain = old_config['domains'][args.domain]
    else:
      domain = {'hosts':{}}
      old_config['domains'][args.domain] = domain
    if args.add:
      if args.remove:
        raise Exception("Only add or remove allowed, not both")
      if not args.name:
        raise Exception("Hostname required for add")
      if not args.ip:
        raise Exception("Ip required for add")
      if not args.octets:
        raise Exception("Octets required when adding a hostname")
      add_host(old_config, args.name + '.' + args.domain, args.ip, domain['hosts'], args.octets)
    elif args.remove:
      if not args.name:
        raise Exception("Hostname required for remove")
      remove_host(old_config, args.name, domain['hosts'])
    print str(domain)
  elif args.options:
    if args.add:
      if not args.name:
        raise Exception("Name required for option add (-n)")
      if not args.value:
        raise Exception("Value required for option value (-v)")
      old_config['options'][args.name] = args.value
    elif args.remove:
      if not args.name:
        raise Exception("Name required for option remove (-n)")
      del old_config['options'][args.name]
    print str(old_config['options'])
  else:
    print str(old_config)
  if not args.temporary:
    save_config(old_config, args.workingFile)
  if args.generate:
    generate_output(old_config, args.folder, args.ip)
