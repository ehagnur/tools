#!/usr/bin/env python2.6
"""
Nagios plugin to check namenode failover. Alerts everytime 
a failover is detected
"""
from HTMLParser import HTMLParser
import argparse
import urllib2
import re
import socket
import sys

# Setup standard Nagios/NRPE return codes
UNKNOWN_STATE = 3
CRITICAL_STATE = 2
WARNING_STATE = 1
OK_STATE = 0

class NNPageParser(HTMLParser):
    """Parse a namenode dfs health page"""

    def __init__(self):
        HTMLParser.__init__(self)
        self.in_h1 = False
        self.nn_host = ""
        self.nn_state = ""

    def handle_starttag(self, tag, attrs):
        if tag == 'h1':
            self.in_h1 = True

    def handle_endtag(self, tag):
        if tag == 'h1':
            self.in_h1 = False

    def handle_data(self, data):
        """Extracts the hostname and state once it gets in to h1 tag"""
        if self.in_h1 and re.match(r'NameNode', data):
            self.nn_host = data.split()[1].split(':')[0].replace('\'', '')
            self.nn_state = data.split()[2].replace('(', '').replace(')', '')

    def save_nn_state(self):
        """Saves the hostname and state in to a file"""
        try:
            with open('/tmp/nn_state.txt', "wb") as fo:
                nn_state_str = "{host} {state}{newline}".format(host=self.nn_host, state=self.nn_state, newline="\n")
                fo.write(nn_state_str)
        except IOError as err:
            print "Exception: Check if /tmp/nn_state.txt file already there. {error}".format(error=err)


def alert_nagios(status, exitcode, text=None):
    """ Send nagios status """
    if text:
        print "{status}: {description}".format(status=status, description=text)
    else:
        print status.upper()
    sys.exit(exitcode)

def main():
    argparser = argparse.ArgumentParser(description="Parses the namenode page for nagios monitoring")
    argparser.add_argument('-H', action="store", dest="hostname")
    args = argparser.parse_args()
    hname = args.hostname
    pageparser = NNPageParser()
    namenode_url = "{prefix}{hostname}{postfix}".format(
        prefix="http://", hostname=hname, postfix=":50070/dfshealth.jsp")
    try:
        request = urllib2.urlopen(namenode_url, timeout=3)
    except urllib2.URLError, e:
        if isinstance(e.reason, socket.timeout):
            print "CRITICAL - Request to {url} timed out".format(url=namenode_url)
            sys.exit(CRITICAL_STATE)
        else:
            msg = "Can't open namenode page. Check the url: {url} is right".format(url=namenode_url)
            alert_nagios("UNKNOWN", UNKNOWN_STATE, msg)
    f = request.read()
    pageparser.feed(f)

    try:
        with open('/tmp/nn_state.txt', "rb") as fo:
            previous_state = fo.read().split()[1].strip()
    except IOError as err:
        msg = "Exception: {error}, ".format(error=str(err))
        pageparser.save_nn_state()
        alert_nagios("UNKNOWN", UNKNOWN_STATE, msg)

    current_state = pageparser.nn_state.strip()

    if previous_state != current_state:
        msg = "{hostname} has changed state from {previous} to {current}".format(
            hostname=pageparser.nn_host, previous=previous_state, current=current_state)
        pageparser.save_nn_state()
        alert_nagios("WARNING", WARNING_STATE, msg)
    elif previous_state == current_state:
        msg = "{hostname} is in the {current} state since last check".format(
            hostname=pageparser.nn_host, current=current_state)
        alert_nagios("OK", OK_STATE, msg)
    else:
        msg = "Cannot determine node state for {hostname}".format(hostname=pageparser.nn_host)
        alert_nagios("UNKNOWN", UNKNOWN_STATE, msg)

if __name__ == '__main__':
    try:
        main()
    except Exception, err:
        msg = "Exception: {error}".format(error=str(err))
        alert_nagios("UNKNOWN", UNKNOWN_STATE, msg)
