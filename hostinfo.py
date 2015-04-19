#!/usr/bin/python
__author__ = 'hsalih'
from socket import gethostbyname
import sys
import requests
import re

class Host():
    '''
    A host class to initialize a host with a hostname and populate with information from ODB
    '''
    def __init__(self, hname):
        self.hostname = hname
    def updatehost(self, hostattr):
        for key in hostattr:
            value = hostattr[key]
            setattr(self, key, value)
    def getvalue(self, hostattr):
        return getattr(self, hostattr)

class ODB:
    def __init__(self, hname):
        self.host = hname
    def getOdbInfo(self):
            odbdict = {}
            try:
                ip = gethostbyname(hname)
                odbURL = "http://jrds.vip.ebay.com/jodbweb/odb.do?type=object&print=adminnotes,adminstatus,assetstatus,fqdn,memory,computeprofile,ostype,oscomputeprofile,serial,tag,vendor&name="+ip+"&format=json"
                resp = requests.get(odbURL)
                data = resp.json()
                hostobj.ipaddress = ip
                for lst in data["objects"][0]["attributes"]:
                    if len(lst) == 2:
                        key = ''.join(lst["name"])
                        if lst["value"] is not None:
                            value = ''.join(lst["value"])
                        else:
                            value = ""
                        #print key, value
                        odbdict[key] = value
                    else:
                        pass
            except (ValueError, KeyError, TypeError):
                    pass
            return odbdict

    def getOdbFunction(self, ip):
        mydict = {}
        odbfuncurl = 'http://jrds.vip.ebay.com/jodbweb/odb.do'

        payload = dict(
                 type='relationship',
                 view='object',
                 name=ip,
                 relationtype='ODB::Link::MemberOf',
                 targettype='ODB::Function',
                 format='json',
                 )
        resp = requests.get(odbfuncurl, params=payload)
        #print resp.url
        data = resp.json()
        name = data['objects'][0]['class'][0]
        value = data['objects'][0]['name'][0]
        mydict[name] = value
        return mydict

    def getOdbAssetInfo(self, ip):
        mydict = {}
        odburl = 'http://jrds.vip.ebay.com/jodbweb/odb.do'

        assetparam = dict(
             type='relationship',
             view='object',
             name=ip,
             relationtype='ODB::Link::LogicalOn',
             targettype='ODB::Asset',
             format='json',
            )

        resp = requests.get(odburl, params=assetparam)
        data = resp.json()
        key = data['objects'][0]['class'][0]
        value = data['objects'][0]['name'][0]
        mydict[key] = value
        return mydict

    def getAssetLocation(self, asset):
        mydict = {}
        odburl = 'http://jrds.vip.ebay.com/jodbweb/odb.do'

        locparam = {
             "type":"object",
             "print": "locationcode",
             "name": asset,
             "format":"json"
            }

        resp = requests.get(odburl, params=locparam)
        data = resp.json()
        lst = data["objects"][0]["attributes"][0]
        if len(lst) == 2:
            key = ''.join(lst["name"])
            if lst["value"] is not None:
                value = ''.join(lst["value"])
            else:
                value = ""
            mydict[key] = value
        else:
            pass
        return mydict


if __name__ == '__main__':
    if len(sys.argv) == 2:
        hname = sys.argv[1]
        hostobj = Host(hname)
        hostodbinfo = ODB(hname)
        odbinfodict = hostodbinfo.getOdbInfo()
        hostobj.updatehost(odbinfodict)
        odbfuncdict = hostodbinfo.getOdbFunction(hostobj.getvalue('ipaddress'))
        hostobj.updatehost(odbfuncdict)
        if hasattr(hostobj, 'vendor'):
            if not re.match(r'.*vm.*',hostobj.getvalue('vendor'),re.I):
                odbipassetdict = hostodbinfo.getOdbAssetInfo(hostobj.getvalue('ipaddress'))
                hostobj.updatehost(odbipassetdict)
                odblocationdict = hostodbinfo.getAssetLocation(hostobj.getvalue('ODB::Asset'))
                hostobj.updatehost(odblocationdict)
        else:
            pass
        print("-"*100)
        for attr, value in sorted(hostobj.__dict__.iteritems()):
            print("%-20s%-s" % (attr+":",value))
        print("-"*100)
    else:
        hname = input("Type hostname and hit return: ")
        hostobj = Host(hname)
        hostodbinfo = ODB(hname)
        odbinfodict = hostodbinfo.getOdbInfo()
        hostobj.updatehost(odbinfodict)
        odbfuncdict = hostodbinfo.getOdbFunction(hostobj.getvalue('ipaddress'))
        hostobj.updatehost(odbfuncdict)
        if hasattr(hostobj, 'vendor'):
            if not re.match(r'.*vm.*',hostobj.getvalue('vendor'),re.I):
                odbipassetdict = hostodbinfo.getOdbAssetInfo(hostobj.getvalue('ipaddress'))
                hostobj.updatehost(odbipassetdict)
                odblocationdict = hostodbinfo.getAssetLocation(hostobj.getvalue('ODB::Asset'))
                hostobj.updatehost(odblocationdict)
        else:
            pass
        print("-"*100)
        for attr, value in sorted(hostobj.__dict__.iteritems()):
            print("%-20s%-s" % (attr+":",value))
        print("-"*100)
