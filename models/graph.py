
EXCLUDED_NODE_KEYS = ['computing_latency', 'position', 'edges', 'edge_net_throughputs', 'edge_net_latencies']

class Graph():
    """ represents a graph """
    
    def __init__(self, nodes, init_graph):
        self.nodes = nodes
        self.graph = self.construct_graph(nodes, init_graph)
        
    def construct_graph(self, nodes, init_graph):
        """
        This method makes sure that the graph is symmetrical. In other words, 
        if there's a path from node A to B with a value V, there needs to be 
        a path from node B to node A with a value V.
        """
        graph = {}
        for node in nodes:
            graph[node] = {}
        
        graph.update(init_graph)
        for node, edges in graph.items():
            for adjacent_node, value in edges.items():
                if adjacent_node not in EXCLUDED_NODE_KEYS:
                    if graph[adjacent_node].get(node, False) == False:
                        pass
                        #TODO: this line is replicating the latency at the destination...
                        #graph[adjacent_node][node] = value 
                    
        return graph
                    
    
    def get_nodes(self):
        "Returns the nodes of the graph."
        return self.nodes
    
    def get_outgoing_edges(self, source_node):
        "Returns the neighbors of a node based."
        neighbours = []
        for out_node in self.nodes:
            if self.graph[source_node].get(out_node, False) != False:
                neighbours.append(out_node)
        
        return neighbours
    
    def get_outgoing_edges_throughput(self, source_node, required_throughput):
        "Returns the neighbors of a node based on throughput availability."
        neighbours = []
        #print(f'\nNodes:')
        #print(self.nodes)
        #print(f'\nGraph:')
        #print(self.graph)
        for out_node in self.nodes:
            if self.graph[source_node].get(out_node, False) != False:
                neighbours.append(out_node)
        
        #print(f'\nneighbours before:')
        #print(neighbours)
        '''
        '''
        for neighbour in neighbours.copy():
            if self.graph[source_node][neighbour]['available_bandwidth'] < required_throughput:
                neighbours.remove(neighbour)
            '''
            #print(f'*** \nchecking neighbour {neighbour} ***')
            if self.graph[source_node][neighbour]['available_bandwidth'] >= required_throughput:
                #print(f'\n{source_node} -> {neighbour} CAN allocate ({required_throughput}) because it has {self.graph[source_node][neighbour]["available_bandwidth"]}')
                pass
            else:
                #print(f'{source_node} -> {neighbour} CANNOT allocate ({required_throughput}) because it has only {self.graph[source_node][neighbour]["available_bandwidth"]}')
                neighbours.remove(neighbour)
                
                #pass
            '''
            
        #print(f'\nneighbours after:')
        #print(neighbours)
        #a = input('')
        return neighbours
    
    def get_computing_latency(self, node1, node2):
        " returns the computing latency between two nodes"
        return self.graph[node1][node2]['computing_latency']

    def get_network_latency(self, node1, node2):
        """ returns the network latency between two nodes"""
        return self.graph[node1][node2]['network_latency']

    def get_network_throughput(self, node1, node2):
        " returns the network throughput between two nodes"
        return self.graph[node1][node2]['network_throughput']
    
    def get_node_computing_latency(self, node):
        """ returns the computing latency of a node """
        return self.graph[node]['computing_latency']
    
    