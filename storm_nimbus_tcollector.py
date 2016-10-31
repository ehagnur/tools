__author__ = 'hsalih'
'''
This tcolelctor runs on storm-master.
Fetches information about the cluster, supervisors and topology stats from nimbus api
The API documentation and all the metrics definition can be found here:
http://storm.apache.org/releases/1.0.1/STORM-UI-REST-API.html
'''
import time
import socket
import requests

class StormTcollector:
    '''
    the constructor is to form the base nimbus api url
    '''
    def __init__(self):
        self.nimbus_host = socket.gethostname()
        self.port = str(8080)
        self.base_url = "http://"+self.nimbus_host+":"+self.port+"/api/v1/"

    def print_metrics(self, metrics_name, tstamp, value, **kwargs):
        '''
        :param metrics_name: the metrics name to be appended to "Storm.cluster" going ot wavefront
        :param tstamp: The time stamp
        :param value: Absolute metrics value
        :param kwargs: Tags, different metrics have different tags. passed as a kwargs
        '''
        tags = []
        for key, val in kwargs.items():
            tag = "{k}={v}".format(k=key, v=val)
            tags.append(str(tag))
        tag_list = " ".join(tags)
        metrics_str = "{name} {ts} {metrics_value} {tags}".format(name="storm.cluster." + metrics_name, ts=tstamp, metrics_value=value, tags=tag_list)
        print metrics_str

    def print_error(self, url, error):
        '''
        This centralized method for url related errors
        :param url: The url failed to open
        :param error: a specific requests Error
        '''
        print "Unable to connect {url} {error}".format(url=url, error=error)
        exit()

    def get_cluster_mertics(self):
        '''
        General cluster level metrics
        '''
        cluster_url = self.base_url + "cluster/summary"
        try:
            clustr_data = requests.get(cluster_url).json()
            ts = int(time.time())
            self.print_metrics("supervisorsTotal", ts, clustr_data['supervisors'])
            self.print_metrics("slotsTotal", ts, clustr_data['slotsTotal'])
            self.print_metrics("slotsUsed", ts, clustr_data['slotsUsed'])
            self.print_metrics("tasksTotal", ts, clustr_data['tasksTotal'])
            self.print_metrics("slotsFree", ts, clustr_data['slotsFree'])
            self.print_metrics("topologiesTotal", ts, clustr_data['topologies'])
        except requests.ConnectionError as err:
            self.print_error(cluster_url, err)

    def get_supervisor_metrics(self):
        '''
        Supervisor level metrics
        '''
        supervisor_url = self.base_url + "supervisor/summary"
        try:
            supervisor_data = requests.get(supervisor_url).json()
            ts = int(time.time())
            for supervisor in supervisor_data['supervisors']:
                self.print_metrics("supervisor.slotsTotal", ts, supervisor['slotsTotal'], host=supervisor['host'])
                self.print_metrics("supervisor.slotsUsed", ts, supervisor['slotsUsed'], host=supervisor['host'])
                self.print_metrics("supervisor.totalMem", ts, supervisor['totalMem'], host=supervisor['host'])
                self.print_metrics("supervisor.usedMem", ts, supervisor['usedMem'], host=supervisor['host'])
                self.print_metrics("supervisor.uptimeMinutes", ts, (supervisor['uptimeSeconds']/60), host=supervisor['host'])
        except requests.ConnectionError as err:
            self.print_error(supervisor_url, err)

    def get_topology_metrics(self):
        '''
        Topology metrics. it will fetch top level topology information and passes the topology id
        to get_topology_info method to get detail stats
        '''
        topology_url = self.base_url + "topology/summary"
        try:
            topology_data = requests.get(topology_url).json()
            ts = int(time.time())
            for topology in topology_data['topologies']:
                self.print_metrics("topologies.assignedMemOnHeap", ts, topology['assignedMemOnHeap'], Topology=topology['name'])
                self.print_metrics("topologies.executorsTotal", ts, topology['executorsTotal'], Topology=topology['name'])
                self.print_metrics("topologies.tasksTotal", ts, topology['tasksTotal'], Topology=topology['name'])
                self.print_metrics("topologies.uptimeMinutes", ts, (topology['uptimeSeconds']/60), Topology=topology['name'])
                self.print_metrics("topologies.workersTotal", ts, topology['workersTotal'], Topology=topology['name'])
                topology_name = topology['name']
                topology_id = topology['id']
                self.get_topology_info(topology_name, topology_id)
        except requests.ConnectionError as err:
            self.print_error(topology_url, err)

    def get_topology_info(self, tname, tid):
        '''
        Gets the topology id from get_topology_metrics method and prints the stat for components and the topology itself.
        Stats are gathered only for components of interest (parser-bolt,aggregator-bolt and kafka-spout) and the values
        are for the last 10 min.
        :param tname:
        :param tid:
        '''
        topology_info_url = self.base_url + "topology/" + tid +"?window=600"
        try:
            topology_info_data = requests.get(topology_info_url).json()
            ts = int(time.time())
            for bolt in topology_info_data['bolts']:
                if bolt['boltId'] == 'parser-bolt' or bolt['boltId'] == 'aggregator-bolt':
                    self.print_metrics("topologies.stat.capacity", ts, bolt['capacity'], Topology=tname, Component=bolt['boltId'])
                    self.print_metrics("topologies.stat.executors", ts, bolt['executors'], Topology=tname, Component=bolt['boltId'])
                    self.print_metrics("topologies.stat.tasks", ts, bolt['tasks'], Topology=tname, Component=bolt['boltId'])
                    self.print_metrics("topologies.stat.acked", ts, bolt['acked'], Topology=tname, Component=bolt['boltId'])
                    self.print_metrics("topologies.stat.executed", ts, bolt['executed'], Topology=tname, Component=bolt['boltId'])
                    self.print_metrics("topologies.stat.transferred", ts, bolt['transferred'], Topology=tname, Component=bolt['boltId'])
                    self.print_metrics("topologies.stat.emitted", ts, bolt['emitted'], Topology=tname, Component=bolt['boltId'])
                else:
                    pass
            for spout in topology_info_data['spouts']:
                if spout['spoutId'] == 'kafka-spout':
                    self.print_metrics("topologies.stat.executors", ts, spout['executors'], Topology=tname, Component=spout['spoutId'])
                    self.print_metrics("topologies.stat.tasks", ts, spout['tasks'], Topology=tname, Component=spout['spoutId'])
                    self.print_metrics("topologies.stat.acked", ts, spout['acked'], Topology=tname, Component=spout['spoutId'])
                    self.print_metrics("topologies.stat.emitted", ts, spout['emitted'], Topology=tname, Component=spout['spoutId'])
                    self.print_metrics("topologies.stat.transferred", ts, spout['transferred'], Topology=tname, Component=spout['spoutId'])
                else:
                    pass
            for stats in topology_info_data['topologyStats']:
                if stats['window'] == 600:
                    self.print_metrics("topologies.stat.acked10m", ts, stats['acked'], Topology=tname)
                    self.print_metrics("topologies.stat.emitted10m", ts, stats['emitted'], Topology=tname)
                    self.print_metrics("topologies.stat.transferred10m", ts, stats['transferred'], Topology=tname)
                else:
                    pass
        except requests.ConnectionError as err:
            self.print_error(topology_info_url, err)


if __name__ == '__main__':
    '''
    Instantiate a StormTcolelctor object gets metrics. Any new metrics can be implemeted as a separate method
    and the same StormTcollector object can be used to run, fetch and send metrics to wavefront
    '''
    try:
        collector_client = StormTcollector()
        collector_client.get_cluster_mertics()
        collector_client.get_supervisor_metrics()
        collector_client.get_topology_metrics()
    except RuntimeError as err:
        print("Unknown error: {error}".format(error=err))