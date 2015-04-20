#!/usr/bin/python
import requests
import urllib.parse
import re
import Host
import argparse

def getbasicinfo(host):
    hostname = host.getvalue('hostname')
    base_url = "xxxxxx"
    ServeParameter = 'xxxxxxxx'

    url = base_url + urllib.parse.quote(ServeParameter)
    #print(url)
    #print(urllib.parse.unquote(url))

    response = requests.get(url)
    data = response.json()["result"][0]
    #print json.dumps(data, indent=3)

    dict = data
    return dict

def getdbhostinfo(host):
    hostname = host.getvalue('hostname')
    print("This fucntion will retrive database related information")

def getlbinfo(host):
    lbname = host.getvalue('hostname')
    print("This function will retrive LB related information")

def printhostattr(host):
    for attr, value in sorted(host.__dict__.iteritems()):
	if not re.match(r'^_.*', attr, re.I|re.M):
	     print("{:20s}{}".format(attr+":", value))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='cms search: ')
    parser.add_argument('hostname')
    parser.add_argument('--verbose', '-v', action='store_true', help='verbose flag')
    parser.add_argument('--database', '-db', action='store_true', help='use this option for database hosts')
    parser.add_argument('--loadbalancer', '-lb', action='store_true', help='use this option for load balancers')

    args = parser.parse_args()

    hostobj = Host.Host(args.hostname)
    hostinfodict = getbasicinfo(host)
    hostobj.updatehost(hostinfodict)
    if args.database:
        getdbhostinfo(hostobj)
    elif args.loadbalancer:
        getlbinfo(hostobj)
    
    printhostattr(hostobj)
