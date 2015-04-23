__author__ = 'hsalih'

from datetime import datetime
import os, os.path
import glob

log_root = "/var/log/tomcat6/"
log_prefix_list = ["catalina.", "localhost.", "host-manager.", "manager."]
now = datetime.now()
for log_prefix in log_prefix_list:
    pattern = log_root + log_prefix + "*"
    print("checking %s" %pattern)
    files = glob.glob(pattern)
    for file in files:
        mtime = datetime.fromtimestamp(os.path.getmtime(file))
        delta = now - mtime
        if delta.days > 30:
            print("file %s was %s days ago, removing" %(file, delta.days))
            os.unlink(file)