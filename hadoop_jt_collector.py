#!/usr/bin/env python2.6
__author__ = 'hsalih'

"""
Collects heap usage and slot information for JobTracker
"""
from HTMLParser import HTMLParser
from xml.etree.ElementTree import fromstring
import urllib2
import re
import time

class JTPageParser(HTMLParser):
    """Collects JT heap usage and slot usage"""

    def __init__(self):
        HTMLParser.__init__(self)
        self.in_h2 = False
        self.jt_heapused = ""
        self.jt_heaptotal = ""
        self.jt_heappercentage = ""

    def handle_starttag(self, tag, attrs):
        if tag == 'h2':
            self.in_h2 = True

    def handle_endtag(self, tag):
        if tag == 'h2':
            self.in_h2 = False

    def handle_data(self, data):
        """Extracts the heap usage"""
        if self.in_h2 and re.match(r'Cluster', data):
            self.jt_heapused = data.split()[5]
            self.jt_heaptotal = data.split()[6].split('/')[1]
            self.jt_heappercentage = (float(self.jt_heapused)/float(self.jt_heaptotal))*100

    def printcollectorvalue(self):
        """print all the collector values"""
        print "{metrics} {tstamp} {value} ".format(metrics="mapred.jobtracker.resource.heap_used_real",tstamp=int(time.time()),value=float(self.jt_heapused))
        print "{metrics} {tstamp} {value} ".format(metrics="mapred.jobtracker.resource.heap_total",tstamp=int(time.time()),value=float(self.jt_heaptotal))
        print "{metrics} {tstamp} {value} ".format(metrics="mapred.jobtracker.resource.heap_used_percent",tstamp=int(time.time()),value=float(self.jt_heappercentage))


def main():
    pageparser = JTPageParser()
    jt_url = "{prefix}{hostname}{postfix}".format(prefix="http://", hostname="dwh-name1005.ve.box.net", postfix=":50030/jobtracker.jsp")

    try:
        request = urllib2.urlopen(jt_url, timeout=10)
    except:
        pass

    f = request.read()
    pageparser.feed(f)

    tree = fromstring(f)
    rows = tree.findall("tr")
    headrow = rows[0]
    datarows = rows[1]

    for num, h in enumerate(headrow):
        data = ", ".join([row[num].text for row in datarows])
        print "{0:<16}: {1}".format(h.text, data)

    pageparser.printcollectorvalue()


if __name__ == '__main__':
    try:
        main()
    except Exception, err:
        pass

