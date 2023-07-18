import typing
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.mec import Mec 
    from models.graph import Graph
    from models.base_station import BaseStation 

from models.dijkstra import Dijkstra
    
""" controller modules """
from controllers import mec_controller

"""other modules"""
import operator
from typing import Dict
from pprint import pprint as pprint

#TODO: here we should have an agnostic method to call these methods, since now we're no long just using dijkstra, but also widest path


class WidestPathController:
    @staticmethod
    def get_widest_path(
        graph: 'Graph', start_node: 'BaseStation', target_node: 'BaseStation' 
    ):
        """gets the widest path (maximum throughput) between start node and the target node"""
        
        previous_nodes, widest_path = Dijkstra.build_widest_path(
            graph, start_node
        )
        
        return Dijkstra.calculate_widest_path(
            previous_nodes, widest_path, start_node, target_node
        )

class DijkstraController:
    def get_shortest_path(
        graph: 'Graph', start_node: 'BaseStation', target_node: 'BaseStation' 
    ):
        """gets the shortest path from one node to all other nodes, where the weights are given in E2E latency"""
        
        previous_nodes, shortest_path = Dijkstra.build_shortest_path(
            graph, start_node
        )
        
        
        
        return Dijkstra.calculate_ETE_shortest_path(
            previous_nodes, shortest_path, start_node, target_node
        )
    
    
    @staticmethod
    def get_all_E2E_shortest_paths(
        graph: 'Graph', start_node: 'BaseStation'
    ):
        
        previous_nodes = None
        shortest_path = None
        
        previous_nodes, shortest_path = Dijkstra.build_E2E_shortest_path(
            graph, start_node
        )
        
        """sorts (ascendent) the shortest path dict into a list of tuples based on latency."""
        sorted_shortest_path = sorted(shortest_path.items(), key=operator.itemgetter(1))
        #print(f'start node: {start_node.bs_name}')
        """The first element is the start node, then the weight is 0"""
        #pprint(sorted_shortest_path)
        #a = input('')
        del sorted_shortest_path[0] 
        #print(f'get all E2E shortest paths')
        #print(sorted_shortest_path)
        #a = input('')
        return sorted_shortest_path
    
    @staticmethod
    def get_ETE_shortest_path(
        graph: 'Graph', start_node: 'BaseStation', target_node: 'BaseStation',  
    ):
        """gets the end-to-end latency between start node and the target node, considering the network latency to reach the target and the computing latency of the target node"""
        
        previous_nodes, shortest_path = Dijkstra.build_E2E_shortest_path(
            graph, start_node
        )
        
        return Dijkstra.calculate_ETE_shortest_path(
            previous_nodes, shortest_path, start_node, target_node
        )
        
    @staticmethod
    def get_shortest_path_with_throughput_restriction(
        graph: 'Graph', start_node: 'BaseStation', target_node: 'BaseStation', required_throughput: float 
    ):
        """gets the end-to-end latency between start node and the target node, considering the network latency to reach the target and the computing latency of the target node"""
        
        previous_nodes, shortest_path = Dijkstra.build_shortest_path_with_throughput_restriction(
            graph, start_node, required_throughput
        )
        
        return Dijkstra.calculate_ETE_shortest_path(
            previous_nodes, shortest_path, start_node, target_node
        )
    
    @staticmethod
    def get_ETE_shortest_path_with_throughput_restriction(
        graph: 'Graph', start_node: 'BaseStation', target_node: 'BaseStation', required_throughput: float 
    ):
        """gets the end-to-end latency between start node and the target node, considering the network latency to reach the target and the computing latency of the target node"""
        
        previous_nodes, shortest_path = Dijkstra.build_E2E_shortest_path_with_throughput_restriction(
            graph, start_node, required_throughput
        )
        
        return Dijkstra.calculate_ETE_shortest_path(
            previous_nodes, shortest_path, start_node, target_node
        )
    
    #TODO: this method should not be called here anymore, instead it should be called from widest_path_controller
    @staticmethod
    def get_widest_path(
        graph: 'Graph', start_node: 'BaseStation', target_node: 'BaseStation', required_throughput: float 
    ):
        """gets the widest path (maximum throughput) between start node and the target node"""
        
        previous_nodes, widest_path = Dijkstra.build_widest_path(
            graph, start_node, required_throughput
        )
        
        return Dijkstra.calculate_widest_path(
            previous_nodes, widest_path, start_node, target_node
        )     
     
    @staticmethod
    def get_ETE_zone_shortest_path(mec_set: Dict[str,'Mec'], graph: 'Graph', start_node: 'BaseStation', zones: bool = False, latency_check: bool = False):
        """gets the shortest path from one node to all other nodes, where the weights are given in E2E latency"""
        
        start_node_mec = mec_controller.MecController.get_mec(mec_set, start_node)
        previous_nodes = None
        shortest_path = None
        
        if zones:
            previous_nodes, shortest_path = Dijkstra.build_ETE_zone_shortest_path(
                graph, start_node, start_node_mec, latency_check
            )
        else:
            previous_nodes, shortest_path = Dijkstra.build_E2E_shortest_path(
                graph, start_node, start_node_mec
            )
        
        """sorts (ascendent) the shortest path dict into a list of tuples based on latency."""
        sorted_widest_path = sorted(shortest_path.items(), key=operator.itemgetter(1))
    
        """The first element is the start node, then the weight is 0"""
        del sorted_widest_path[0] 
        return sorted_widest_path
    
    ################################################################################################
    
    
    def get_shortest_path_all_paths(
        graph: 'Graph', start_node: 'BaseStation', base_station_set: Dict[str,'BaseStation']
    ):
        """gets the shortest path from one node to all other nodes, where the weights are given in E2E latency"""
        print(f'\n################ SHORTEST PATH (NET LATENCY) ################\n')
        previous_nodes, shortest_path = Dijkstra.build_shortest_path(
            graph, start_node
        )
        
        candidates = {}
        min_net_latency = 100000
        for node, net_latency in shortest_path.items():
            if node != start_node.bs_name:
                
                if net_latency == min_net_latency:
                    candidates[node] = net_latency
                
                elif net_latency < min_net_latency:
                    candidates.clear()
                    candidates[node] = net_latency
                    min_net_latency = net_latency 
        
        shortest_path[start_node.bs_name] = '---'
        #print(f'\nPrevious Nodes')
        #pprint(previous_nodes)
        print(f'\nAll Shortest Path')
        pprint(shortest_path)
        #print(f'\nCandidates')
        #pprint(candidates)
        
        target_node_id = list(candidates.keys())[0]
        target_node_id = target_node_id[2:]
        target_node = base_station_set[target_node_id]
        
        path, distance =  Dijkstra.calculate_ETE_shortest_path(
            previous_nodes, shortest_path, start_node, target_node
        )
        print(f'\n')
        
        print(" -> ".join(path))
        print(f'with cost {distance}')
    
    def get_E2E_shortest_path_all_paths(
        graph: 'Graph', start_node: 'BaseStation', base_station_set: Dict[str,'BaseStation']
    ):
        """gets the shortest path from one node to all other nodes, where the weights are given in E2E latency"""
        print(f'\n################ E2E SHORTEST PATH (E2E LATENCY) ################\n')
        previous_nodes, shortest_path = Dijkstra.build_E2E_shortest_path(
            graph, start_node
        )
        
        candidates = {}
        min_net_latency = 100000
        for node, net_latency in shortest_path.items():
            if node != start_node.bs_name:
                
                if net_latency == min_net_latency:
                    candidates[node] = net_latency
                
                elif net_latency < min_net_latency:
                    candidates.clear()
                    candidates[node] = net_latency
                    min_net_latency = net_latency 
        
        #shortest_path[start_node.bs_name] = '---'
        #print(f'\nPrevious Nodes')
        #pprint(previous_nodes)
        print(f'\nAll Shortest Paths')
        pprint(shortest_path)
        #print(f'\nCandidates')
        #pprint(candidates)
        
        target_node_id = list(candidates.keys())[0]
        target_node_id = target_node_id[2:]
        target_node = base_station_set[target_node_id]
        
        path, distance =  Dijkstra.calculate_ETE_shortest_path(
            previous_nodes, shortest_path, start_node, target_node
        )
        print(f'\n')
        
        print(" -> ".join(path))
        print(f'with cost {distance}')
                
    @staticmethod
    def get_E2E_throughput_widest_path_all_paths(
        graph: 'Graph', base_station_set: Dict[str,'BaseStation'], start_node: 'BaseStation', required_throughput: float
    ):
        """calculates the end-to-end throughput between start node and the target node"""
        print(f'\n################ WIDEST PATH (BANDWIDTH) ################\n')
        previous_nodes, widest_path = Dijkstra.build_widest_path(
            graph, start_node, required_throughput
        )
        candidates = {}
        max_throughput = 0
        for node, bandwidth in widest_path.items():
            if node != start_node.bs_name:
                
                if bandwidth == max_throughput:
                    candidates[node] = bandwidth
                
                elif bandwidth > max_throughput:
                    candidates.clear()
                    candidates[node] = bandwidth
                    max_throughput = bandwidth 
        
        widest_path[start_node.bs_name] = '---'
        #print(f'\nPrevious Nodes')
        #pprint(previous_nodes)
        #print(f'\nAll Widest Paths')
        #pprint(widest_path)
        print(f'\nCandidates')
        pprint(candidates)  
        
        for node, bandwidth in candidates.items():
            target_node_id = node
            target_node_id = target_node_id[2:]
            target_node = base_station_set[target_node_id]
            
            path, distance =  Dijkstra.calculate_widest_path(
                previous_nodes, widest_path, start_node, target_node
            )
            print(f'\n')
            
            print(" -> ".join(path))
            print(f'with cost {distance}')
    
    
    @staticmethod
    def get_E2E_throughput_widest_path_all_paths_without_restrictions(
        graph: 'Graph', start_node: 'BaseStation', base_station_set: Dict[str,'BaseStation']
    ):
        """calculates the end-to-end throughput between start node and the target node"""
        print(f'\n################ WIDEST PATH (BANDWIDTH) ################\n')
        previous_nodes, widest_path = Dijkstra. build_widest_path_without_bw_restriction(
            graph, start_node
        )
        candidates = {}
        max_throughput = 0
        for node, bandwidth in widest_path.items():
            if node != start_node.bs_name:
                
                if bandwidth == max_throughput:
                    candidates[node] = bandwidth
                
                elif bandwidth > max_throughput:
                    candidates.clear()
                    candidates[node] = bandwidth
                    max_throughput = bandwidth 
        
        widest_path[start_node.bs_name] = '---'
        #print(f'\nPrevious Nodes')
        #pprint(previous_nodes)
        #print(f'\nAll Widest Paths')
        #pprint(widest_path)
        print(f'\nCandidates')
        pprint(candidates)  
        
        for node, bandwidth in candidates.items():
            target_node_id = node
            target_node_id = target_node_id[2:]
            target_node = base_station_set[target_node_id]
            
            path, distance =  Dijkstra.calculate_widest_path(
                previous_nodes, widest_path, start_node, target_node
            )
            print(f'\n')
            
            print(" -> ".join(path))
            print(f'with cost {distance}')
    
   