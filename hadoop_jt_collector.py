#!/usr/bin/env python2.6
__author__ = 'hsalih'
"""
Collects heap usage and slot information for JobTracker
"""
import re
from bs4 import BeautifulSoup
import urllib
import time
import socket

def main():
    header_list = []
    value_list = []
    resource_dict = {}
    hostname = socket.gethostname()
    jt_url = "{prefix}{host}{postfix}".format(prefix="http://", host=hostname, postfix=":50030/jobtracker.jsp")
    request = urllib.urlopen(jt_url).read()
    soup = BeautifulSoup(request)
    heap = soup.find_all("h2")
    resource_dict["heap_used_real"] = heap[0].text.split()[5]
    resource_dict["heap_total"] = heap[0].text.split()[6].split('/')[1]
    resource_dict["heap_used_percentage"] = (float(heap[0].text.split()[5])/float(heap[0].text.split()[6].split('/')[1]))*100
    slot_usage = soup.find_all("table")[0]
    rows = slot_usage.findAll('tr')

    for tr in rows:
        for th in tr.findAll("th"):
            header_list.append(re.sub(r'\s|/|\.',"_",th.findNext(text=True)))
        for td in tr.findAll("td"):
            value_list.append(td.findNext(text=True))

    for item in range(len(header_list)):
            resource_dict[header_list[item]] = value_list[item]

    for key in resource_dict:
        printmetrics(key,resource_dict[key])

def printmetrics(name, value):
    """print all the collector values"""
    print "{metrics} {tstamp} {value} ".format(metrics="mapred.jobtracker.resource."+name,tstamp=int(time.time()),value=float(value))

if __name__ == '__main__':
    try:
        main()
    except:
        pass
