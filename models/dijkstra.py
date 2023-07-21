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
    """represents the Dijkstra algorithm for service migration"""
    
    @staticmethod 
    def build_shortest_path(graph: 'Graph', start_node: 'BaseStation'):
        """builds the shortest path based on the network latency"""
        
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
        dist[start_node.bs_name] = 0#start_node.wireless_latency #+ start_node_mec.computing_latency  
        
        # print(f'\nsource node: {start_node.bs_name}')
        it = 0
        while unvisited_nodes:
            """finds the node with the lowest score"""
            current_min_node = None
            for node in unvisited_nodes: 
                if current_min_node == None:
                    current_min_node = node
                elif dist[node] < dist[current_min_node]:
                    current_min_node = node
                    
                    
            # print(f'\n\ncurrent min node: {current_min_node}')
            #print(f'current max node: {current_max_node}')
            """retrieves the current node's neighbors and updates their distances"""
            neighbors = graph.get_outgoing_edges(current_min_node)
            for neighbor in neighbors:
                it += 1
                if neighbor in unvisited_nodes:
                    # print(f'\nneighbor: {neighbor}')
                    new_distance = dist[current_min_node] + graph.get_network_latency(current_min_node, neighbor)
                    # print(f'new distance: {new_distance}')
                    if new_distance < dist[neighbor]:
                        # print(f'new distance: {new_distance} < dist[neighbor]: {dist[neighbor]}')
                        # print(f'updating dist[neighbor]({dist[neighbor]}) to {new_distance}')
                        dist[neighbor] = round(new_distance, 2)
                        """We also update the best path to the current node"""
                        previous_nodes[neighbor] = current_min_node
                        # print(f'updating previous_nodes[neighbor] to {current_min_node}')
                
            """After visiting its neighbors, we mark the node as 'visited'"""
            unvisited_nodes.remove(current_min_node)

        #pprint(dist)
        #pprint(previous_nodes)
        # print(f'\n***iterations: {it}\n')
        return previous_nodes, dist
    
    @staticmethod 
    def build_shortest_path_bk(graph: 'Graph', start_node: 'BaseStation'):
        """builds the shortest path based on the network latency"""
        
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
        dist[start_node.bs_name] = 0#start_node.wireless_latency #+ start_node_mec.computing_latency  
        
        print(f'\nsource node: {start_node.bs_name}')
        
        while unvisited_nodes:
            """finds the node with the lowest score"""
            current_min_node = None
            for node in unvisited_nodes: 
                if current_min_node == None:
                    current_min_node = node
                elif dist[node] < dist[current_min_node]:
                    current_min_node = node
            print(f'\n\ncurrent min node: {current_min_node}')
            """retrieves the current node's neighbors and updates their distances"""
            neighbors = graph.get_outgoing_edges(current_min_node)
            for neighbor in neighbors:
                if neighbor in unvisited_nodes:
                    print(f'\nneighbor: {neighbor}')
                    new_distance = dist[current_min_node] + graph.get_network_latency(current_min_node, neighbor)
                    print(f'new distance: {new_distance}')
                    if new_distance < dist[neighbor]:
                        print(f'new distance: {new_distance} < dist[neighbor]: {dist[neighbor]}')
                        print(f'updating dist[neighbor]({dist[neighbor]}) to {new_distance}')
                        dist[neighbor] = round(new_distance, 2)
                        """We also update the best path to the current node"""
                        previous_nodes[neighbor] = current_min_node
                        print(f'updating previous_nodes[neighbor] to {current_min_node}')
                
            """After visiting its neighbors, we mark the node as 'visited'"""
            unvisited_nodes.remove(current_min_node)
        from pprint import pprint as pprint
        pprint(dist)
        pprint(previous_nodes)
        return previous_nodes, dist
    
    
    @staticmethod 
    def build_E2E_shortest_path(graph: 'Graph', start_node: 'BaseStation'):
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
        dist[start_node.bs_name] = start_node.node_latency  
        
        """The algorithm executes until we visit all nodes"""
        while unvisited_nodes:
            """The code block below finds the node with the lowest score"""
            current_min_node = None
            for node in unvisited_nodes: 
                if current_min_node == None:
                    current_min_node = node
                elif dist[node] < dist[current_min_node]:
                    current_min_node = node
            
            """The code block below retrieves the current node's neighbors and updates their distances"""
            neighbors = graph.get_outgoing_edges(current_min_node)
           
            for neighbor in neighbors:
                if neighbor in unvisited_nodes:
                    new_distance = (dist[current_min_node] - graph.get_node_computing_latency(current_min_node) + graph.get_network_latency(current_min_node, neighbor) + graph.get_node_computing_latency(neighbor))
                    
                    if new_distance < dist[neighbor]:
                        dist[neighbor] = round(new_distance, 2)
                        """We also update the best path to the current node"""
                        previous_nodes[neighbor] = current_min_node
                   
            """After visiting its neighbors, we mark the node as 'visited'"""            
            unvisited_nodes.remove(current_min_node)
            
        return previous_nodes, dist
    
    @staticmethod 
    def build_shortest_path_with_throughput_restriction(graph: 'Graph', start_node: 'BaseStation', required_throughput: float):
        """builds the shortest path based on the network latency"""
        
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
        dist[start_node.bs_name] = start_node.wireless_latency 
        
        """The algorithm executes until we visit all nodes"""
        while unvisited_nodes:
            """The code block below finds the node with the lowest score"""
            current_min_node = None
            for node in unvisited_nodes: 
                if current_min_node == None:
                    current_min_node = node
                elif dist[node] < dist[current_min_node]:
                    current_min_node = node
              
            """The code block below retrieves the current node's neighbors and updates their distances"""
            neighbors = graph.get_outgoing_edges_throughput(current_min_node, required_throughput)
            for neighbor in neighbors:
                if neighbor in unvisited_nodes:
                    new_distance = dist[current_min_node] + graph.get_network_latency(current_min_node, neighbor)
                    if new_distance < dist[neighbor]:
                        dist[neighbor] = round(new_distance, 2)
                        """We also update the best path to the current node"""
                        previous_nodes[neighbor] = current_min_node
                
            """After visiting its neighbors, we mark the node as 'visited'"""
            unvisited_nodes.remove(current_min_node)
        return previous_nodes, dist
    
    @staticmethod 
    def build_E2E_shortest_path_with_throughput_restriction(graph: 'Graph', start_node: 'BaseStation', required_throughput: float):
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
        dist[start_node.bs_name] = start_node.wireless_latency + start_node.node_latency  
        
        """The algorithm executes until we visit all nodes"""
        while unvisited_nodes:
            """The code block below finds the node with the lowest score"""
            current_min_node = None
            for node in unvisited_nodes: 
                if current_min_node == None:
                    current_min_node = node
                elif dist[node] < dist[current_min_node]:
                    current_min_node = node
            
            """The code block below retrieves the current node's neighbors and updates their distances"""
            neighbors = graph.get_outgoing_edges_throughput(current_min_node, required_throughput)
           
            for neighbor in neighbors:
                if neighbor in unvisited_nodes:
                    new_distance = (dist[current_min_node] - graph.get_node_computing_latency(current_min_node) + graph.get_network_latency(current_min_node, neighbor) + graph.get_node_computing_latency(neighbor))
                    
                    if new_distance < dist[neighbor]:
                        dist[neighbor] = round(new_distance, 2)
                        """We also update the best path to the current node"""
                        previous_nodes[neighbor] = current_min_node
                   
            """After visiting its neighbors, we mark the node as 'visited'"""            
            unvisited_nodes.remove(current_min_node)
            
        return previous_nodes, dist
    
    @staticmethod 
    def build_widest_path(graph: 'Graph', start_node: 'BaseStation'):
        """builds the shortest path based on the E2E throughput"""
        #print(f'\nsource node: {start_node.bs_name}')
        unvisited_nodes = list(graph.get_nodes()) 
        """
        We'll use this dict to save the cost of visiting each node and update it as we move along the graph. 
        This variable is similar to dist in the standard Dijkstra's algorithm.
        """   
        dist = {}
    
        """We'll use this dict to save the shortest known path to a node found so far"""
        previous_nodes = {}
    
        """We'll use min_value to initialize the value of the unvisited nodes"""   
        min_value = -10**9
        
        """We'll use min_value to initialize the start node"""
        max_value = 10**9
        
        for node in unvisited_nodes:
            dist[node] = min_value
            
        """We initialize the  starting node with 0"""   
        dist[start_node.bs_name]= max_value
        
        while unvisited_nodes:
            """finds the node with the highest bw score"""
            current_max_node = None
            for node in unvisited_nodes: 
                if current_max_node == None:
                    current_max_node = node
                elif dist[node] > dist[current_max_node]:
                    current_max_node = node
              
            """retrieves the current node's neighbors and updates their throughputs"""
            
            neighbors = graph.get_outgoing_edges(current_max_node)
           
            
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
                        """We also update the best path to the current node"""
                        previous_nodes[neighbor] = current_max_node
                                    
            """After visiting its neighbors, we mark the node as 'visited'"""
            unvisited_nodes.remove(current_max_node)       
        return previous_nodes, dist
    
    @staticmethod 
    def build_widest_path_without_bw_restriction(graph: 'Graph', start_node: 'BaseStation'):
        """builds the shortest path based on the E2E throughput"""
        #print(f'\nsource node: {start_node.bs_name}')
        unvisited_nodes = list(graph.get_nodes()) 
        """
        We'll use this dict to save the cost of visiting each node and update it as we move along the graph. 
        This variable is similar to dist in the standard Dijkstra's algorithm.
        """   
        dist = {}
    
        """We'll use this dict to save the shortest known path to a node found so far"""
        previous_nodes = {}
    
        """We'll use min_value to initialize the value of the unvisited nodes"""   
        min_value = -10**9
        
        """We'll use min_value to initialize the start node"""
        max_value = 10**9
        
        for node in unvisited_nodes:
            dist[node] = min_value
            
        """We initialize the  starting node with 0"""   
        dist[start_node.bs_name]= max_value
        
        """The algorithm executes until we visit all nodes"""
        while unvisited_nodes:
            """The code block below finds the node with the lowest score"""
            current_max_node = None
            for node in unvisited_nodes: 
                if current_max_node == None:
                    current_max_node = node
                elif dist[node] > dist[current_max_node]:
                    current_max_node = node
              
            """The code block below retrieves the current node's neighbors and updates their throughputs"""
            #print(f'\nCurrent max node: {current_max_node}')
            neighbors = graph.get_outgoing_edges(current_max_node)
           
            
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
                        """We also update the best path to the current node"""
                        previous_nodes[neighbor] = current_max_node
                                
            """After visiting its neighbors, we mark the node as 'visited'"""
            unvisited_nodes.remove(current_max_node)       
        return previous_nodes, dist
        
    @staticmethod 
    def build_ETE_zone_shortest_path(graph: 'Graph', start_node: 'BaseStation', start_node_mec: 'Mec', latency_check: bool):
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
        dist[start_node.name] = start_node.wireless_latency + start_node_mec.computing_latency  
        
        """current_min_node is the start_node instead of the node with the lowest latency """
        current_min_node = start_node.name
        neighbors = graph.get_outgoing_edges(current_min_node)
        
        """ we define a zone searching arround the start_node's neighbors """
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
    
    
        
    ########################################################################    
        
    @staticmethod
    def calculate_ETE_shortest_path( 
        previous_nodes, shortest_path, start_node: 'BaseStation', target_node: 'BaseStation'
    ):
        """ returns the shortest path (lowest ETE latency) between the source and destination node and the path cost """
        path = []
        node = target_node.bs_name
        
        while node != start_node.bs_name:
            path.append(node)
            if node in previous_nodes:
                node = previous_nodes[node]
            else:
                break
    
        """ Adds the start node manually """
        path.append(start_node.bs_name)
        
        path.reverse()
        return path, round(shortest_path[target_node.bs_name], 2)


    @staticmethod
    def calculate_widest_path( 
        previous_nodes, widest_path, start_node: 'BaseStation', target_node: 'BaseStation'
    ):
        """ returns the widest path (throughput) between the source and destination node and the path cost """
        
        path = []
        node = target_node.bs_name
        
        while node != start_node.bs_name:
            path.append(node)
            if node in previous_nodes:
                node = previous_nodes[node]
            else:
                break
    
        """ Adds the start node manually """
        path.append(start_node.bs_name)
        
        #print(f'we found the following best path from {start_node.name} with a value of {shortest_path[target_node.name]}')
        #print(" -> ".join(reversed(path)))
        
        path.reverse()
        return path, widest_path[target_node.bs_name]

    









