import typing
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.mec import Mec 
    from models.graph import Graph
    from models.base_station import BaseStation 

from models.paths import Dijkstra, WidestPath, FLATWISE, SCG_Dijkstra
    
""" controller modules """
from controllers import mec_controller
from controllers import network_controller

"""other modules"""
import sys
import operator
from typing import Dict
from pprint import pprint as pprint


class PathController:
    
    ########################  WIDEST PATH ########################
    @staticmethod
    def get_widest_path(
        graph: 'Graph', source_node: 'BaseStation', target_node: 'BaseStation', required_throughput: float  
    ):
        previous_nodes, widest_path = WidestPath.build_widest_path(
            graph, source_node, required_throughput
        )
        
        return PathController.calculate_path(
            previous_nodes, widest_path, source_node, target_node
        )
        
    ########################  SHORTEST PATH ########################

    @staticmethod
    def get_shortest_path(
        graph: 'Graph', source_node: 'BaseStation', target_node: 'BaseStation', required_throughput: float  
    ):  
        previous_nodes, shortest_path = Dijkstra.build_shortest_path(
            graph, source_node, required_throughput
        )
        
        return PathController.calculate_path(
            previous_nodes, shortest_path, source_node, target_node
        )
        
    ########################  FLATWISE SHORTST PATH ########################
        
    @staticmethod
    def get_flatwise_path(
        base_station_set: Dict[str, 'BaseStation'], graph: 'Graph', source_node: 'BaseStation', target_node: 'BaseStation', latency_requirement: float, required_throughput: float,   
    ):  
        previous_nodes, shortest_path = FLATWISE.build_FLATWISE_path(
            base_station_set, 
            graph, 
            source_node, 
            target_node, 
            latency_requirement, 
            required_throughput
        )
        
        return PathController.calculate_path(
            previous_nodes, shortest_path, source_node, target_node
        )
    
    ########################  WIDEST SHORTEST PATH ########################
    
    @staticmethod
    def _calculate_widest_shortest_path(graph: 'Graph', paths: list):
        """ get the widest shortest path with the highest throughput among all candidate paths"""
        wsp_path = 0
        wsp_cost = 0
        wsp_throughput = 0
        
        for path in paths:
            route_throughput = network_controller.NetworkController.get_route_net_throughput(graph, path[0])
            
            if route_throughput > wsp_throughput:
                wsp_path = path[0]
                wsp_cost = path[1]
                wsp_throughput = route_throughput
        
        return wsp_path, wsp_cost
        
    @staticmethod
    def get_widest_shortest_path(
        graph: 'Graph', source_node: 'BaseStation', target_node: 'BaseStation', required_throughput: float  
    ):  
        previous_nodes, widest_shortest_path = Dijkstra.build_widest_shortest_path(
            graph, source_node, required_throughput
        )
        
        paths =  PathController.calculate_paths(
            previous_nodes, widest_shortest_path, source_node, target_node
        )
        
        if not paths:
            return None, None
        
        return PathController._calculate_widest_shortest_path(graph, paths)
        
        
    ########################  SHORTEST WIDEST PATH ########################
        
    @staticmethod
    def _calculate_shortest_widest_path(graph: 'Graph', paths: list):
        """ get the shortest widest path with the lowest latency cost among all candidate paths"""
        
        swp_path = 0
        swp_cost = 0
        swp_latency = sys.maxsize
        
        for path in paths:
            route_latency = network_controller.NetworkController.get_route_net_latency(graph, path[0])
            
            if route_latency < swp_latency:
                swp_path = path[0]
                swp_cost = path[1]
                swp_latency = route_latency
        
        return swp_path, swp_cost
        
    @staticmethod
    def get_shortest_widest_path(
        graph: 'Graph', source_node: 'BaseStation', target_node: 'BaseStation', required_throughput: float  
    ):  
        previous_nodes, shortest_widest_path = WidestPath.build_shortest_widest_path(
            graph, source_node, required_throughput
        )
        
        paths =  PathController.calculate_paths(
            previous_nodes, shortest_widest_path, source_node, target_node
        )
        
        if not paths:
            return None, None
        
        return PathController._calculate_shortest_widest_path(graph, paths)
    
    ########################  SINGLE PATH CALCULATION ########################
    
    @staticmethod
    def calculate_path( 
        previous_nodes, calculated_path, start_node: 'BaseStation', target_node: 'BaseStation'
    ):
        """ returns the route and cost for any shortest or widest path between the source and destination node"""
            
        path = []
        node = target_node.bs_name
        if node not in previous_nodes:
            return None, None
        
        while node != start_node.bs_name:
            path.append(node)
            if node in previous_nodes:
                node = previous_nodes[node]
            else:
                break
    
        path.append(start_node.bs_name)
        path.reverse()
        return path, round(calculated_path[target_node.bs_name], 2)
    
    ########################  MULTIPLE PATH CALCULATION ########################
    
    @staticmethod
    def calculate_paths(previous_nodes, calculated_distances, start_node: 'BaseStation', target_node: 'BaseStation'):
        """Returns the routes and costs for all shortest paths between the source and destination node"""
        # pprint(previous_nodes)
        def build_path(node, target_node):
            path = [target_node]
            while node != start_node.bs_name:
                path.append(node)
                if node in previous_nodes:
                    node = previous_nodes[node][0]  # Pick one of the potential previous nodes
                else:
                    break
            path.append(start_node.bs_name)
            path.reverse()
            return path

        paths = []
        
        if target_node.bs_name not in previous_nodes:
            return None
            
        for node in previous_nodes[target_node.bs_name]:
            path = build_path(node, target_node.bs_name)
            paths.append((path, round(calculated_distances[target_node.bs_name], 2)))

        return paths




class Others:
    
    @staticmethod
    def get_all_E2E_shortest_paths(
        graph: 'Graph', source_node: 'BaseStation'
    ):
        
        previous_nodes = None
        shortest_path = None
        
        previous_nodes, shortest_path = SCG_Dijkstra.build_E2E_shortest_path(
            graph, source_node
        )
        
        """sorts (ascendent) the shortest path dict into a list of tuples based on latency."""
        sorted_shortest_path = sorted(shortest_path.items(), key=operator.itemgetter(1))
        #print(f'start node: {source_node.bs_name}')
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
        graph: 'Graph', source_node: 'BaseStation', target_node: 'BaseStation',  
    ):
        """gets the end-to-end latency between start node and the target node, considering the network latency to reach the target and the computing latency of the target node"""
        
        previous_nodes, shortest_path = SCG_Dijkstra.build_E2E_shortest_path(
            graph, source_node, 1
        )
        
        return PathController.calculate_path(
            previous_nodes, shortest_path, source_node, target_node
        )
        
    @staticmethod
    def get_shortest_path_with_throughput_restriction(
        graph: 'Graph', source_node: 'BaseStation', target_node: 'BaseStation', required_throughput: float 
    ):
        """gets the end-to-end latency between start node and the target node, considering the network latency to reach the target and the computing latency of the target node"""
        
        previous_nodes, shortest_path = Dijkstra.build_shortest_path_with_throughput_restriction(
            graph, source_node, required_throughput
        )
        
        return Dijkstra.calculate_ETE_shortest_path(
            previous_nodes, shortest_path, source_node, target_node
        )
    
    @staticmethod
    def get_ETE_shortest_path_with_throughput_restriction(
        graph: 'Graph', source_node: 'BaseStation', target_node: 'BaseStation', required_throughput: float 
    ):
        """gets the end-to-end latency between start node and the target node, considering the network latency to reach the target and the computing latency of the target node"""
        
        previous_nodes, shortest_path = Dijkstra.build_E2E_shortest_path_with_throughput_restriction(
            graph, source_node, required_throughput
        )
        
        return Dijkstra.calculate_ETE_shortest_path(
            previous_nodes, shortest_path, source_node, target_node
        )
    
    #TODO: this method should not be called here anymore, instead it should be called from widest_path_controller
    @staticmethod
    def get_widest_path(
        graph: 'Graph', source_node: 'BaseStation', target_node: 'BaseStation', required_throughput: float 
    ):
        """gets the widest path (maximum throughput) between start node and the target node"""
        
        previous_nodes, widest_path = Dijkstra.build_widest_path(
            graph, source_node, required_throughput
        )
        
        return Dijkstra.calculate_widest_path(
            previous_nodes, widest_path, source_node, target_node
        )     
     
    @staticmethod
    def get_ETE_zone_shortest_path(mec_set: Dict[str,'Mec'], graph: 'Graph', source_node: 'BaseStation', zones: bool = False, latency_check: bool = False):
        """gets the shortest path from one node to all other nodes, where the weights are given in E2E latency"""
        
        start_node_mec = mec_controller.MecController.get_mec(mec_set, source_node)
        previous_nodes = None
        shortest_path = None
        
        if zones:
            previous_nodes, shortest_path = Dijkstra.build_ETE_zone_shortest_path(
                graph, source_node, start_node_mec, latency_check
            )
        else:
            previous_nodes, shortest_path = Dijkstra.build_E2E_shortest_path(
                graph, source_node, start_node_mec
            )
        
        """sorts (ascendent) the shortest path dict into a list of tuples based on latency."""
        sorted_widest_path = sorted(shortest_path.items(), key=operator.itemgetter(1))
    
        """The first element is the start node, then the weight is 0"""
        del sorted_widest_path[0] 
        return sorted_widest_path
    
    ################################################################################################
    
    
    def get_shortest_path_all_paths(
        graph: 'Graph', source_node: 'BaseStation', base_station_set: Dict[str,'BaseStation']
    ):
        """gets the shortest path from one node to all other nodes, where the weights are given in E2E latency"""
        print(f'\n################ SHORTEST PATH (NET LATENCY) ################\n')
        previous_nodes, shortest_path = Dijkstra.build_shortest_path(
            graph, source_node
        )
        
        candidates = {}
        min_net_latency = 100000
        for node, net_latency in shortest_path.items():
            if node != source_node.bs_name:
                
                if net_latency == min_net_latency:
                    candidates[node] = net_latency
                
                elif net_latency < min_net_latency:
                    candidates.clear()
                    candidates[node] = net_latency
                    min_net_latency = net_latency 
        
        shortest_path[source_node.bs_name] = '---'
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
            previous_nodes, shortest_path, source_node, target_node
        )
        print(f'\n')
        
        print(" -> ".join(path))
        print(f'with cost {distance}')
    
    def get_E2E_shortest_path_all_paths(
        graph: 'Graph', source_node: 'BaseStation', base_station_set: Dict[str,'BaseStation']
    ):
        """gets the shortest path from one node to all other nodes, where the weights are given in E2E latency"""
        print(f'\n################ E2E SHORTEST PATH (E2E LATENCY) ################\n')
        previous_nodes, shortest_path = Dijkstra.build_E2E_shortest_path(
            graph, source_node
        )
        
        candidates = {}
        min_net_latency = 100000
        for node, net_latency in shortest_path.items():
            if node != source_node.bs_name:
                
                if net_latency == min_net_latency:
                    candidates[node] = net_latency
                
                elif net_latency < min_net_latency:
                    candidates.clear()
                    candidates[node] = net_latency
                    min_net_latency = net_latency 
        
        #shortest_path[source_node.bs_name] = '---'
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
            previous_nodes, shortest_path, source_node, target_node
        )
        print(f'\n')
        
        print(" -> ".join(path))
        print(f'with cost {distance}')
                
    @staticmethod
    def get_E2E_throughput_widest_path_all_paths(
        graph: 'Graph', base_station_set: Dict[str,'BaseStation'], source_node: 'BaseStation', required_throughput: float
    ):
        """calculates the end-to-end throughput between start node and the target node"""
        print(f'\n################ WIDEST PATH (BANDWIDTH) ################\n')
        previous_nodes, widest_path = Dijkstra.build_widest_path(
            graph, source_node, required_throughput
        )
        candidates = {}
        max_throughput = 0
        for node, bandwidth in widest_path.items():
            if node != source_node.bs_name:
                
                if bandwidth == max_throughput:
                    candidates[node] = bandwidth
                
                elif bandwidth > max_throughput:
                    candidates.clear()
                    candidates[node] = bandwidth
                    max_throughput = bandwidth 
        
        widest_path[source_node.bs_name] = '---'
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
                previous_nodes, widest_path, source_node, target_node
            )
            print(f'\n')
            
            print(" -> ".join(path))
            print(f'with cost {distance}')
    
    
    @staticmethod
    def get_E2E_throughput_widest_path_all_paths_without_restrictions(
        graph: 'Graph', source_node: 'BaseStation', base_station_set: Dict[str,'BaseStation']
    ):
        """calculates the end-to-end throughput between start node and the target node"""
        print(f'\n################ WIDEST PATH (BANDWIDTH) ################\n')
        previous_nodes, widest_path = Dijkstra. build_widest_path_without_bw_restriction(
            graph, source_node
        )
        candidates = {}
        max_throughput = 0
        for node, bandwidth in widest_path.items():
            if node != source_node.bs_name:
                
                if bandwidth == max_throughput:
                    candidates[node] = bandwidth
                
                elif bandwidth > max_throughput:
                    candidates.clear()
                    candidates[node] = bandwidth
                    max_throughput = bandwidth 
        
        widest_path[source_node.bs_name] = '---'
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
                previous_nodes, widest_path, source_node, target_node
            )
            print(f'\n')
            
            print(" -> ".join(path))
            print(f'with cost {distance}')
    
   