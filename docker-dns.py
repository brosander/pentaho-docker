import json
from subprocess import Popen, PIPE
import sys
from twisted.application import service, internet
from twisted.internet import defer
from twisted.names import cache, client, dns, server
from twisted.names.common import ResolverBase
from twisted.names.error import DNSQueryRefusedError

TTL=30

def getRunningContainers():
  #docker ps | tail -n +2 | awk '{print $1}' | xargs docker inspect
  p1 = Popen(['docker', 'ps'], stdout = PIPE)
  p2 = Popen(['tail', '-n', '+2'], stdin = p1.stdout, stdout = PIPE)
  p3 = Popen(['awk', '{print $1}'], stdin = p2.stdout, stdout = PIPE)
  inspectCall = ['docker', 'inspect']
  inspectCall.extend(p3.communicate()[0].strip().split())
  result = {}
  if len(inspectCall) > 2:
    p4 = Popen(inspectCall, stdout = PIPE)
    containers = json.loads(p4.communicate()[0].decode(sys.stdout.encoding))
    for container in containers:
      result[container['Config']['Hostname']] = container['NetworkSettings']['IPAddress']
      result['.'.join(reversed(container['NetworkSettings']['IPAddress'].split('.'))) + '.in-addr.arpa'] = container['Config']['Hostname']
  return result

def getIpAddress(interface):
  #ifconfig eth0 | grep "inet addr" | awk '{print $2}' | sed 's/addr://g'
  p1 = Popen(['ifconfig', interface], stdout = PIPE)
  p2 = Popen(['grep', 'inet addr'], stdin = p1.stdout, stdout = PIPE)
  p3 = Popen(['awk', '{print $2}'], stdin = p2.stdout, stdout = PIPE)
  p4 = Popen(['sed', 's/addr://g'], stdin = p3.stdout, stdout = PIPE)
  return p4.communicate()[0].decode(sys.stdout.encoding).strip()

class ContainerResolver(client.Resolver):
  def __init__(self):
    client.Resolver.__init__(self, servers=[('208.67.222.222',53), ('208.67.220.220', 53)])

  def _lookup(self, name, cls, type, timeout):
    containers = getRunningContainers()
    if name in containers:
      if name.endswith('.in-addr.arpa'):
        return defer.succeed(([dns.RRHeader(name = name, ttl = TTL, payload = dns.Record_PTR(name = containers[name], ttl = TTL), auth = True, type=type)], (), ()))
      else:
        return defer.succeed(([dns.RRHeader(name = name, ttl = TTL, payload = dns.Record_A(containers[name], ttl = TTL), auth = True)], (), ()))
    print "Falling back to default impl"
    return client.Resolver._lookup(self, name, cls, type, timeout)
    #return defer.fail(DNSQueryRefusedError("Not a docker hostname"))

#  def lookupAddress(self, name, timeout = None):
#    print "Lookup address received for: " + name
#    containers = getRunningContainers()
#    if name in containers:
#      return defer.succeed(([dns.RRHeader(name = name, ttl = TTL, payload = dns.Record_A(containers[name], ttl = TTL), auth = True)], (), ()))
#    else:
#      return defer.fail()
      #return self._lookup(name, dns.IN, dns.A, timeout)

application = service.Application('dnsserver', 1, 1)

# create the protocols
f = server.DNSServerFactory(caches=[cache.CacheResolver()], clients=[ContainerResolver()])
p = dns.DNSDatagramProtocol(f)
f.noisy = p.noisy = False

# register as tcp and udp
ret = service.MultiService()
PORT=53

for (klass, arg) in [(internet.TCPServer, f), (internet.UDPServer, p)]:
  s = klass(PORT, arg, interface = getIpAddress('eth0'))
  s.setServiceParent(ret)

# run all of the above as a twistd application
ret.setServiceParent(service.IServiceCollection(application))

# run it through twistd!
if __name__ == '__main__':
  import sys
  print "Usage: twistd -y %s" % sys.argv[0]
