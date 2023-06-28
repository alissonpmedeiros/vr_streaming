import typing 
if typing.TYPE_CHECKING:    
    """ model modules"""
    from models.mec import Mec as Mec
    from models.base_station import BaseStation as BaseStation

from models.graph import Graph as Graph
from pprint import pprint as pprint
""" controller modules """
#from controllers import bs_controller 
#from controllers import mec_controller 
 

"""other modules"""
from typing import Dict


class GraphController:
    
    ''' 
    @staticmethod
    def allocate_bandwidth(
        graph: Graph, source: 'BaseStation', destination: 'BaseStation', bandwidth: float
    ):
        """allocates bandwidth in the graph"""
        """ 
        1. get the widest path between source and destination
        2. check if the required bandwidth is available at each path
        3. If so, allocate the bandwidth
        4. Otherwise, we have to calculate another widest path by excluding the paths that have no available bandwidth
        
        """
        
        
        
        source_name = source.bs_name
        destination_name = destination.bs_name
        graph.graph[source_name][destination_name]['allocated_bandwidth'] += bandwidth
        graph.graph[source_name][destination_name]['available_banwidth'] -= bandwidth
        
    '''
        
    
    @staticmethod
    def print_graph(graph: Graph):
        pprint(graph.graph)
    
    @staticmethod
    def get_graph(base_station_set: Dict[str,'BaseStation']) -> Graph:
        """ constructs the graph based on the base station and mec servers data """
        
        nodes = []
        for bs_id, base_station in base_station_set.items():
            nodes.append(base_station.bs_name)
        
        """ init the graph with base stations ids """
        init_graph = {}
        for node in nodes:
            init_graph[node] = {}

        """ adds the destinations on each source node and the network latency (weight) between them """
        for src_bs_id, src_bs in base_station_set.items():
            src_bs_name = src_bs.bs_name
            bs_mec_latency = src_bs.node_latency
            init_graph[src_bs_name]['computing_latency'] = bs_mec_latency
            init_graph[src_bs_name]['position'] = src_bs.position
            init_graph[src_bs_name]['edges'] = src_bs.edges
            init_graph[src_bs_name]['edge_net_latencies'] = src_bs.edge_net_latencies
            init_graph[src_bs_name]['edge_net_throughputs'] = src_bs.edge_net_throughputs
            for dst in src_bs.edges:
                dst_name = base_station_set[dst].bs_name
                edge_index = src_bs.edges.index(dst)
                dst_net_latency = src_bs.edge_net_latencies[edge_index]
                dst_net_throughput = src_bs.edge_net_throughputs[edge_index]
                dst_node_latency = base_station_set[dst].node_latency
                
                init_graph[src_bs_name][dst_name] = {
                    'network_latency': dst_net_latency,
                    'network_throughput': dst_net_throughput,
                    'computing_latency': dst_node_latency,
                    'available_bandwidth': dst_net_throughput,
                    'initial_available_bw': dst_net_throughput,
                    'allocated_bandwidth': 0
                }
                
        """ constructs the graph """
        graph = Graph(nodes, init_graph)
        return graph


