import typing
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.mec import Mec 
    from models.graph import Graph
    from models.base_station import BaseStation 

""" controller modules """
from controllers import config_controller
from controllers import network_controller
    
""" other modules """
import sys, math, heapq
from pprint import pprint as pprint


CONFIG = config_controller.ConfigController.get_config()
ETE_LATENCY_THRESHOLD = CONFIG['SYSTEM']['ETE_LATENCY_THRESHOLD']

class Dijkstra:
    
    @staticmethod
    def build_shortest_path(graph: 'Graph', start_node: 'BaseStation', required_throughput: float):
        """builds the shortest path based on the network latency"""
        
        unvisited_nodes = list(graph.get_nodes())
        dist = {}
        previous_nodes = {}
    
    
        max_value = sys.maxsize
        for node in unvisited_nodes:
            dist[node] = max_value
            
        dist[start_node.bs_name] = 0 
        
        while unvisited_nodes:
            current_min_node = None
            for node in unvisited_nodes: 
                if current_min_node == None:
                    current_min_node = node
                elif dist[node] < dist[current_min_node]:
                    current_min_node = node
                       
                    
            neighbors = graph.get_outgoing_edges_throughput(current_min_node, required_throughput)
            for neighbor in neighbors:
                if neighbor in unvisited_nodes:
                    new_distance = dist[current_min_node] + graph.get_network_latency(current_min_node, neighbor)
                    if new_distance < dist[neighbor]:
                        dist[neighbor] = round(new_distance, 2)
                        previous_nodes[neighbor] = current_min_node
                        
            unvisited_nodes.remove(current_min_node)

        return previous_nodes, dist
    
    @staticmethod 
    def build_widest_shortest_path(graph: 'Graph', source_node: 'BaseStation', required_throughput: float):
        """ we first determine the shortest path. In case two paths have the same weight, we choose the one with the highest throughput"""
        
        unvisited_nodes = list(graph.get_nodes())
        dist = {}
        previous_nodes = {}
    
    
        max_value = sys.maxsize
        for node in unvisited_nodes:
            dist[node] = max_value
            
        dist[source_node.bs_name] = 0 
        
        while unvisited_nodes:
            current_min_node = None
            for node in unvisited_nodes: 
                if current_min_node == None:
                    current_min_node = node
                elif dist[node] < dist[current_min_node]:
                    current_min_node = node
                       
                    
            neighbors = graph.get_outgoing_edges_throughput(current_min_node, required_throughput)
            for neighbor in neighbors:
                if neighbor in unvisited_nodes:
                    new_distance = dist[current_min_node] + graph.get_network_latency(current_min_node, neighbor)
                    
                    if new_distance < dist[neighbor]:
                        dist[neighbor] = round(new_distance, 2)
                        previous_nodes[neighbor] = [current_min_node]
                    
                    elif new_distance == dist[neighbor]:
                        previous_nodes[neighbor].append(current_min_node)
                        
            unvisited_nodes.remove(current_min_node)

        return previous_nodes, dist
    
    
    
    
    
class WidestPath:
    
    @staticmethod 
    def build_widest_path(graph: 'Graph', source_node: 'BaseStation', required_throughput: float):
        """builds the widest path based on throughput"""
        unvisited_nodes = list(graph.get_nodes()) 
        dist = {}
        previous_nodes = {}
    
        """We'll use min_value to initialize the value of the unvisited nodes"""   
        min_value = -10**9
        
        """We'll use min_value to initialize the start node"""
        max_value = 10**9
        
        for node in unvisited_nodes:
            dist[node] = min_value
            
        dist[source_node.bs_name]= max_value
        
        while unvisited_nodes:
            # pprint(dist)
            current_max_node = None
            for node in unvisited_nodes: 
                if current_max_node == None:
                    current_max_node = node
                elif dist[node] > dist[current_max_node]:
                    current_max_node = node

            #     elif dist[node] == dist[current_max_node]:
            #         print(f'current_max_node candidates: {current_max_node}, {node})')    
            
            # print(f'\ncurrent_max_node: {current_max_node}')  
            # a = input('')
                
            neighbors = graph.get_outgoing_edges_throughput(current_max_node, required_throughput)        
            
            for neighbor in neighbors:
                if neighbor in unvisited_nodes:
                    new_distance = max(
                        dist[neighbor], 
                        min(
                            dist[current_max_node], 
                            graph.get_network_available_throughput(current_max_node, neighbor)
                        )
                    )
                    if new_distance > dist[neighbor]:
                        dist[neighbor] = round(new_distance, 2)
                        previous_nodes[neighbor] = current_max_node
                                    
            unvisited_nodes.remove(current_max_node) 
            
        return previous_nodes, dist
    
    @staticmethod
    def build_shortest_widest_path(graph: 'Graph', source_node: 'BaseStation', required_throughput: float):
        """ we first determine the widest path. In case two paths have the same weight, we choose the one with the lowest latency"""
        
        unvisited_nodes = list(graph.get_nodes()) 
        dist = {}
        previous_nodes = {}
    
        """We'll use min_value to initialize the value of the unvisited nodes"""   
        min_value = -10**9
        
        """We'll use min_value to initialize the start node"""
        max_value = 10**9
        
        for node in unvisited_nodes:
            dist[node] = min_value
            
        dist[source_node.bs_name]= max_value
        
        while unvisited_nodes:
            current_max_node = None
            for node in unvisited_nodes: 
                if current_max_node == None:
                    current_max_node = node
                elif dist[node] > dist[current_max_node]:
                    current_max_node = node
                
            neighbors = graph.get_outgoing_edges_throughput(current_max_node, required_throughput)
            
            for neighbor in neighbors:
                if neighbor in unvisited_nodes:
                    new_distance = max(
                        dist[neighbor], 
                        min(
                            dist[current_max_node], 
                            graph.get_network_throughput(current_max_node, neighbor)
                        )
                    )
                    
                    if new_distance > dist[neighbor]:
                        dist[neighbor] = round(new_distance, 2)
                        previous_nodes[neighbor] = [current_max_node] 
                    
                    elif new_distance == dist[neighbor]:
                        previous_nodes[neighbor].append(current_max_node)   
                                    
            unvisited_nodes.remove(current_max_node)       
        
        return previous_nodes, dist
    


        
    
    
   
        
        
        
        
class SCG_Dijkstra:    
        
    @staticmethod 
    def build_ETE_zone_shortest_path(graph: 'Graph', source_node: 'BaseStation', source_node_mec: 'Mec', latency_check: bool):
        """builds the shortest path based on the ETE latency"""
        
        unvisited_nodes = list(graph.get_nodes()) 
        """
        We'll use this dict to save the cost of visiting each node and update it as we move along the graph. 
        This variable is similar to dist in the standard Dijkstra's algorithm.
        """   
        dist = {}
    
        """We'll use this dict to save the shortest known path to a node found so far"""
        previous_nodes = {}
    
        """We'll use max_value to initialize the "infinity" value of the unvisited nodes"""   
        max_value = sys.maxsize
        for node in unvisited_nodes:
            dist[node] = max_value
            
        """However, we initialize the  starting node with wireless latency of the Base station to reach the attached MEC and the computing latency of the MEC """   
        dist[source_node.name] = source_node.wireless_latency + source_node_mec.computing_latency  
        
        """current_min_node is the source_node instead of the node with the lowest latency """
        current_min_node = source_node.name
        neighbors = graph.get_outgoing_edges(current_min_node)
        
        """ we define a zone searching arround the source_node's neighbors """
        for neighbor in neighbors:
            if neighbor in unvisited_nodes:
                tentative_value = (dist[current_min_node] - graph.get_node_computing_latency(current_min_node) + graph.get_network_latency(current_min_node, neighbor) + graph.get_node_computing_latency(neighbor))
                if tentative_value < dist[neighbor]:
                    dist[neighbor] = tentative_value
                    """We also update the best path to the current node"""
                    previous_nodes[neighbor] = current_min_node
                
                if latency_check and tentative_value <= ETE_LATENCY_THRESHOLD:
                    return previous_nodes, dist
            
        return previous_nodes, dist
    
    
    @staticmethod 
    def build_E2E_shortest_path(graph: 'Graph', source_node: 'BaseStation', required_throughput: float):
        """builds the shortest path based on the ETE latency"""
        
        unvisited_nodes = list(graph.get_nodes())   
        dist = {}
        previous_nodes = {}
    
        max_value = sys.maxsize
        for node in unvisited_nodes:
            dist[node] = max_value
            
        """However, we initialize the  starting node with wireless latency of the Base station to reach the attached MEC and the computing latency of the MEC """   
        dist[source_node.bs_name] = source_node.node_latency  
        
        while unvisited_nodes:
            current_min_node = None
            for node in unvisited_nodes: 
                if current_min_node == None:
                    current_min_node = node
                elif dist[node] < dist[current_min_node]:
                    current_min_node = node
            
            neighbors = graph.get_outgoing_edges_throughput(current_min_node, required_throughput)
           
            for neighbor in neighbors:
                if neighbor in unvisited_nodes:
                    new_distance = (dist[current_min_node] - graph.get_node_computing_latency(current_min_node) + graph.get_network_latency(current_min_node, neighbor) + graph.get_node_computing_latency(neighbor))
                    
                    if new_distance < dist[neighbor]:
                        dist[neighbor] = round(new_distance, 2)
                        previous_nodes[neighbor] = current_min_node
                   
            unvisited_nodes.remove(current_min_node)
                        
        return previous_nodes, dist
        
    


    

    









