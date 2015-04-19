__author__ = 'hsalih'

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
