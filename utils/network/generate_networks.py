import os
import numpy as np
import networkx as nx
#import plotly.io as pio   
import os, json, random
from scipy import spatial
import matplotlib.pyplot as plt
import plotly.graph_objects as go
#pio.kaleido.scope.mathjax = None
from pprint import pprint as pprint
import matplotlib
#matplotlib.use('TkAgg')

import json
from json import JSONEncoder
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json

TOPOLOGIES = {
    'geneva': {
        'nodes': 269,
        'radius': [0.08],
        'edges:': [726],
        'ALVP':   [2.7 ]
    }
}

#Bern
#CITY = 'bern'
#RADIUS = 0.2
#NUMBER_NODES = 50

CITY = 'geneva'
RADIUS = 0.09
NUMBER_NODES = 269

#networkx plot 

'''
# for small graphs
NODE_SIZE = 800
NODE_FONT_SIZE = 8
EDGE_FONT_SIZE = 8
'''

# for medium graphs
'''
NODE_SIZE = 500
NODE_FONT_SIZE = 7
EDGE_FONT_SIZE = 7

'''
# for large graphs
NODE_SIZE = 90
NODE_FONT_SIZE = 6
#EDGE_FONT_SIZE = 4
EDGE_FONT_SIZE = 6



FONT_FAMILY="sans-serif"
NODE_FONT_COLOR = 'white'
VERTICAL_ALIGNMENT = 'center'

#plotly
PLOTLY_NODE_SIZE = 24
PLOTLY_NODE_FONT = 'Arial'
EDGE_LINE_WIDTH = 1
EDGE_LINE_COLOR = '#888'
LEGEND_FONT_SIZE = 90
LEGEND_COLOR = 'black'


@dataclass_json
@dataclass
class Node:
    id: str
    bs_name: str
    node_label: str
    node_latency: float
    wireless_latency: float
    signal_range: float
    position: list = field(default_factory=list, init=True)
    edges: list = field(default_factory=list, init=False)
    edge_net_latencies: list = field(default_factory=list, init=False)
    edge_net_throughputs: list = field(default_factory=list, init=False)
    
    edge_net_throughputs: list = field(default_factory=list, init=False)
    edge_net_throughputs: list = field(default_factory=list, init=False)
        
class DiGraph:
    def __init__(self) -> None:
        self.graph = nx.DiGraph()
        self.graph_positions = {}
        self.custom_names = {}
        self.nodes_set = {}

class Graph:
    def __init__(self) -> None:    
        self.graph = nx.Graph()
        self.baseline_positions = []
        
####################################################################

def generate_positions(number_nodes):
    positions =  np.random.rand(number_nodes,2)
    return positions

def generate_graph_connections(graph: Graph):
    #forces the graph to be a connected graph
    
    while True:
        positions = generate_positions(NUMBER_NODES)
        kdtree = spatial.KDTree(positions)
        pairs = kdtree.query_pairs(RADIUS)
        
        graph.graph.add_nodes_from(range(NUMBER_NODES))
        graph.graph.add_edges_from(list(pairs))
        
        
        if nx.is_connected(graph.graph):
            graph.baseline_positions = positions
            print(f'NODES: {graph.graph.number_of_nodes()} | EDGES: {graph.graph.number_of_edges()} | ALPV: {graph.graph.number_of_edges()/graph.graph.number_of_nodes()}')
        
            print('Graph is connected!')
            break
            
        else:    
            print('\nGraph is not connected!')
            graph.graph = nx.Graph()
        
def init_graph(graph: Graph, di_graph: DiGraph, node_latency, net_latency_threshold, net_throughput_threshold):
    """ initialize di_graph based on graph information """
    
    #creates custom names for the nodes bases on the node id and its computing latency
    for node in graph.graph.nodes():
        computing_latency = round(
            random.uniform(node_latency['lower_latency_threshold'], node_latency['upper_latency_threshold']), 2
        )
        node_label = str(node) + '\n(' + str(computing_latency) + ')'
        di_graph.custom_names[node] = node_label
        
        wireless_latency = round(random.uniform(0.1, 0.3), 2)
        signal_range = 0.13

        # adds nodes and their positions from BASELINE GRAPH to GRAPH
        x_pos = graph.baseline_positions[node][0] 
        y_pos = graph.baseline_positions[node][1] 
        
        node_position = []
        node_position.append(x_pos)
        node_position.append(y_pos)
        
        bs_name = 'BS' + str(node)
        
        new_node = Node(node, bs_name, node_label, computing_latency, wireless_latency, signal_range, node_position)
        di_graph.nodes_set[node] = new_node
        
        di_graph.graph.add_node(di_graph.custom_names[node],pos=(x_pos,y_pos))
        node_position = np.array(graph.baseline_positions[node], dtype=np.float32)
        di_graph.graph_positions[di_graph.custom_names[node]] = node_position
    
    # inserts edges from BASELINE GRAPH into GRAPH
    for edge in graph.graph.edges():
        src = edge[0]
        dst = edge[1]
        
        net_latency = round(
            random.uniform(net_latency_threshold['lower_latency_threshold'], net_latency_threshold['upper_latency_threshold']), 2
        )
          
        net_throughput = round(
            random.uniform(net_throughput_threshold['lower_throughput_threshold'], net_throughput_threshold['upper_throughput_threshold']), 2
        )
        
        # updating source throughput and latency in node_set  
        di_graph.nodes_set[src].edges.append(str(dst))
        di_graph.nodes_set[src].edge_net_latencies.append(net_latency)
        di_graph.nodes_set[src].edge_net_throughputs.append(net_throughput)
        
        # updating destination throughput and latency in node_set
        di_graph.nodes_set[dst].edges.append(str(src))
        di_graph.nodes_set[dst].edge_net_latencies.append(net_latency)
        di_graph.nodes_set[dst].edge_net_throughputs.append(net_throughput)
        
        di_graph.graph.add_edge(
            u_of_edge=di_graph.custom_names[src], 
            v_of_edge=di_graph.custom_names[dst], 
            net_latency=net_latency
        )
        
          
        di_graph.graph.add_edge(
            u_of_edge=di_graph.custom_names[src], 
            v_of_edge=di_graph.custom_names[dst], 
            net_throughput=net_throughput
        )

def create_topology(file_dir, file_name, pdf_name):
    graph = Graph()
    di_graph = DiGraph()
    
    node_latency = {'lower_latency_threshold': 2, 'upper_latency_threshold': 5}
    net_latency = {'lower_latency_threshold': 0.5, 'upper_latency_threshold': 1}
    net_throughput = {'lower_throughput_threshold': 5000, 'upper_throughput_threshold': 100000}
    
    generate_graph_connections(graph)
    init_graph(graph, di_graph, node_latency, net_latency, net_throughput)
    save_to_json(di_graph, file_dir, file_name)
    while True:    
        draw_graph(di_graph, pdf_name)

#####################################################################
        
def draw_graph(di_graph: DiGraph, pdf_name, throughput=False):
    """ draws the GRAPH """
    
    if throughput:
        #edges = [(u, v) for (u, v, d) in di_graph.graph.edges(data=True)]
        
        esmall = [(u, v) for (u, v, d) in di_graph.graph.edges(data=True) if d["net_available_throughput"] < (d["net_throughput"] * 0.3)]
        
        neutral = [(u, v) for (u, v, d) in di_graph.graph.edges(data=True) if d["net_available_throughput"] >= (d["net_throughput"] * 0.3) and d["net_available_throughput"] <= (d["net_throughput"] * 0.8)]
                   
        elarge = [(u, v) for (u, v, d) in di_graph.graph.edges(data=True) if d["net_available_throughput"] > ((d["net_throughput"] * 0.8))]
        
        
        #pprint(di_graph.graph_positions)
        #pprint(di_graph.graph.graph)
        #a = input('')
        # nodes
        nx.draw_networkx_nodes(di_graph.graph, di_graph.graph_positions, node_size=NODE_SIZE)
        
        # node labels
        '''
        '''
        nx.draw_networkx_labels(
            di_graph.graph, 
            di_graph.graph_positions, 
            font_color=NODE_FONT_COLOR, 
            font_size=NODE_FONT_SIZE, 
            font_family=FONT_FAMILY, 
            verticalalignment=VERTICAL_ALIGNMENT
        )
        
        # edges
        nx.draw_networkx_edges(
            di_graph.graph, di_graph.graph_positions, 
            edgelist=esmall, 
            width=0.8, 
            style="dashed", 
            edge_color="r",
            #connectionstyle='arc3, rad = -0.3', 
            arrows=None, 
            arrowstyle='-'
        )
        nx.draw_networkx_edges(
            di_graph.graph, di_graph.graph_positions, 
            edgelist=elarge, 
            width=0.8, 
            alpha=0.5, 
            edge_color="g", 
            style="dashed", 
            #connectionstyle='arc3, rad = 0.3', 
            arrows=None, 
            arrowstyle='-'
        )
        nx.draw_networkx_edges(
            di_graph.graph, di_graph.graph_positions, 
            edgelist=neutral, 
            width=0.8, 
            alpha=0.5, 
            edge_color="b", 
            style="dashed", 
            #connectionstyle='arc3, rad = 0.3', 
            arrows=None, 
            arrowstyle='-'
        )
        
        # edge throughput labels
        net_allocated_throughput = nx.get_edge_attributes(di_graph.graph, "net_allocated_throughput")
        net_available_throughput = nx.get_edge_attributes(di_graph.graph, "net_available_throughput")
        net_throughput = nx.get_edge_attributes(di_graph.graph, "net_throughput")
        net_throughput_labels = {}
        
        #converting throughputs from Mbps to Gbps
        for k, v in net_throughput.copy().items():
            net_throughput[k] = round(v/1000, 2)
            
        #converting throughputs from Mbps to Gbps
        for k, v in net_allocated_throughput.copy().items():
            net_allocated_throughput[k] = round(v/1000, 2)
            
        #converting throughputs from Mbps to Gbps
        for k, v in net_available_throughput.copy().items():
            net_available_throughput[k] = round(v/1000, 2)
        
        '''
        zipped = zip(net_throughput.items(), net_allocated_throughput.items(), net_available_throughput.items())
        zipped_list = list(zipped)
        for z in zipped_list:
            print(z)
            a = input('')
        al = input('')
        '''
        
        for (t, al, av) in zip(net_throughput.items(), net_allocated_throughput.items(), net_available_throughput.items()):
            node_id = t[0]
            #net_throughput_labels[node_id] = 'T(' + str(t[1]) + ')' + 'AL(' + str(al[1]) + ')'  + 'AV(' + str(av[1]) + ')'
            #net_throughput_labels[node_id] = 'A('+str(av[1])+')'
            net_throughput_labels[node_id] = str(av[1])
        
        nx.draw_networkx_edge_labels(
            di_graph.graph, 
            di_graph.graph_positions, 
            net_throughput_labels, 
            font_size=EDGE_FONT_SIZE
        )
        
    else:    
        
        # provides different colors for each link according to their throughput
        elarge = [(u, v) for (u, v, d) in di_graph.graph.edges(data=True) if d["net_throughput"] < (10000 * 0.3)]
        
        neutral = [(u, v) for (u, v, d) in di_graph.graph.edges(data=True) if d["net_throughput"] >= (10000 * 0.3) and d["net_throughput"] <= (10000 * 0.8)]
                   
        esmall = [(u, v) for (u, v, d) in di_graph.graph.edges(data=True) if d["net_throughput"] > ((10000 * 0.8))]
        
        # provides different colors for each link according to their latency
        '''
        esmall = [(u, v) for (u, v, d) in di_graph.graph.edges(data=True) if d["net_latency"] < 0.7]
        neutral = [(u, v) for (u, v, d) in di_graph.graph.edges(data=True) if d["net_latency"] >= 0.7 and d["net_latency"] <= 0.8]
        elarge = [(u, v) for (u, v, d) in di_graph.graph.edges(data=True) if d["net_latency"] > 0.8]
        '''
        
        #pprint(di_graph.graph_positions)
        #pprint(di_graph.graph.graph)
        #al = input('')
        
        # nodes
        nx.draw_networkx_nodes(di_graph.graph, di_graph.graph_positions, node_size=NODE_SIZE)
        
        # node labels
        '''
        '''
        nx.draw_networkx_labels(
            di_graph.graph, 
            di_graph.graph_positions, 
            font_color=NODE_FONT_COLOR, 
            font_size=NODE_FONT_SIZE, 
            font_family=FONT_FAMILY, 
            verticalalignment=VERTICAL_ALIGNMENT
        )

        # edges
        nx.draw_networkx_edges(
            di_graph.graph, di_graph.graph_positions, 
            edgelist=elarge, 
            width=0.8, 
            style="dashed", 
            edge_color="r",
            #connectionstyle='arc3, rad = -0.3', 
            arrows=None, 
            arrowstyle='-'
        )
        nx.draw_networkx_edges(
            di_graph.graph, di_graph.graph_positions, 
            edgelist=esmall, 
            width=0.8, 
            alpha=0.5, 
            edge_color="g", 
            style="dashed", 
            #connectionstyle='arc3, rad = 0.3', 
            arrows=None, 
            arrowstyle='-'
        )
        nx.draw_networkx_edges(
            di_graph.graph, di_graph.graph_positions, 
            edgelist=neutral, 
            width=0.8, 
            alpha=0.5, 
            edge_color="b", 
            style="dashed", 
            #connectionstyle='arc3, rad = 0.3', 
            arrows=None, 
            arrowstyle='-'
        )
    
        # edge latency and throughput labels
        net_allocated_throughput = nx.get_edge_attributes(di_graph.graph, "net_latency")
        throughput_labels = nx.get_edge_attributes(di_graph.graph, "net_throughput")
        
        #converting throughputs from Mbps to Gbps
        for k, v in throughput_labels.copy().items():
            throughput_labels[k] = round(v/1000, 2)
            
            
        net_latency_throughput_labels = {}
        
        for (k,v), (k2,v2) in zip(net_allocated_throughput.items(), throughput_labels.items()):
            #plot latency labels only
            #net_latency_throughput_labels[k] = str(v) #+ '\n(' + str(v2) + ')'
            
            #plot throughput labels only
            net_latency_throughput_labels[k] = str(v2) 
        
        nx.draw_networkx_edge_labels(
            di_graph.graph, 
            di_graph.graph_positions, 
            net_latency_throughput_labels, 
            font_size=EDGE_FONT_SIZE
        )
    
    ax = plt.gca()
    ax.margins(0.00)
    plt.axis("off")
    plt.tight_layout()
    '''
    '''
    
    #a = input('enter to continue')

    #plt.savefig(pdf_name, bbox_inches='tight', orientation='landscape', dpi=None)  
    #plt.show(block=False)
    #plt.draw()
    #plt.show(block=False)
    #plt.pause(0.005)
    
    #plt.imshow(plt.imread(pdf_name))
    plt.pause(5)
    plt.clf()
    
def draw_plotly_graph(m_graph: DiGraph):
    edge_x = []
    edge_y = []
    for edge in m_graph.graph.edges():
        x0, y0 = m_graph.graph.nodes[edge[0]]['pos']
        x1, y1 = m_graph.graph.nodes[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)


    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=EDGE_LINE_WIDTH, color=EDGE_LINE_COLOR),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    for node in m_graph.graph.nodes():
        x, y = m_graph.graph.nodes[node]['pos']
        node_x.append(x)
        node_y.append(y)


    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=PLOTLY_NODE_SIZE, # node size
            colorbar=dict(
                thickness=20,
                tickcolor='black',
                tickfont=dict(size=LEGEND_FONT_SIZE, color='black', family=PLOTLY_NODE_FONT),
                title=dict(
                    text='Node Connections', 
                    font=dict(
                        size=LEGEND_FONT_SIZE, 
                        color=LEGEND_COLOR, 
                        family=PLOTLY_NODE_FONT
                    )
                ),
                xanchor='left',
                titleside='right'
            ),
            line_width=3))

    node_adjacencies = []
    node_text = []
    for node, adjacencies in enumerate(m_graph.graph.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        node_text.append('# of connections: '+str(len(adjacencies[1])))

    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text

    fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                    title='<br>',
                    titlefont_size=26,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    fig.update_layout(coloraxis={"colorbar":{"dtick":1}})
    '''
    fig.update_layout(
                  xaxis = dict(
                    tickmode='array', #change 1
                    tickvals = x, #change 2
                    ticktext = [0,2,4,6,8], #change 3
                    ),
                   font=dict(size=18, color="black"))
    '''
    fig.write_image("./plotly_network_topology.pdf", format="pdf", width=1980, height=1080)
    
    #fig.show()
        
def save_to_json(di_graph: DiGraph, file_dir, file_name):
    
    encoded_node_set = {
        'base_station_set': {}
    }
    
    for id, node in di_graph.nodes_set.items():
        encoded_node_set['base_station_set'][id] = node.__dict__
    
    print(f'\n*** encoding ***\n')
    with open("{}{}".format(file_dir, file_name), "w+") as file_write:
        json.dump(encoded_node_set, file_write, indent=2, ensure_ascii=False)
    
    return 


def load_topology(data_dir, file_name, pdf_name):
    '''loads the graph from json file'''
    
    di_graph = DiGraph() 
    
    data = {}
    with open("{}{}".format(data_dir, file_name)) as json_file:
        data = json.loads(json_file.read())
    
    data = data['base_station_set']
    
    for node_id, node_data in data.items():
        #updating graph to be stored in the json file
        
        node_latency = node_data['node_latency']
        bs_name = node_data['bs_name']
        signal_range = node_data['signal_range']
        node_label = str(node_id) + '\n(' + str(node_latency) + ')'
        node_position = node_data['position']     
        
        new_node = Node(node_id, bs_name, node_label, node_latency, signal_range, node_position)
        di_graph.nodes_set[node_id] = new_node
        
        
        #updating the graph to be drawn
        x_pos = node_position[0]
        y_pos = node_position[1]
        
        di_graph.graph.add_node(node_label,pos=(x_pos, y_pos))
        node_position_aux = np.array(node_position, dtype=np.float32)
        di_graph.graph_positions[node_label] = node_position_aux
        
        
        
    for node_id, node_data in data.items():
        for edge in node_data['edges']:
            edge_index = node_data['edges'].index(edge)
            src = node_id
            dst = str(edge)
            
            edge_net_latencies = node_data['edge_net_latencies']
            net_latency = edge_net_latencies[edge_index]
            
            edge_net_throughputs = node_data['edge_net_throughputs']
            net_throughput = edge_net_throughputs[edge_index]
            
            # updating source throughput and latency in node_set  
            di_graph.nodes_set[src].edges.append(dst)
            di_graph.nodes_set[src].edge_net_latencies.append(net_latency)
            di_graph.nodes_set[src].edge_net_throughputs.append(net_throughput)
            
            # updating destination throughput and latency in node_set
            #di_graph.nodes_set[dst].edges.append(src)
            #di_graph.nodes_set[dst].edge_net_latencies.append(net_latency)
            #di_graph.nodes_set[dst].edge_net_throughputs.append(net_throughput)
            
            #print(type(src))
            #print(type(dst))
            
            #a = input('')
            #pprint(di_graph.nodes_set[src])
            #print(f'##############################################################')
            #pprint(di_graph.nodes_set[dst])
            src_name = di_graph.nodes_set[src].node_label
            dst_name = di_graph.nodes_set[dst].node_label
            
            # updating source throughput and latency accordingly
            di_graph.graph.add_edge(
                u_of_edge=src_name, 
                v_of_edge=dst_name, 
                net_latency=net_latency, 
                net_throughput=net_throughput
            )
            
            # updating destination throughput and latency accordingly
            di_graph.graph.add_edge(
                u_of_edge=dst_name, 
                v_of_edge=src_name, 
                net_latency=net_latency, 
                net_throughput=net_throughput
            )
    
    while True:           
        draw_graph(di_graph, pdf_name)
    #file_name = CITY + '_r_' + str(RADIUS) + '.json'
    
    
    #save_to_json(di_graph, file_dir, 'NEW.json')
    #a = input('')
    #draw_plotly_graph(m_graph)


@staticmethod
def plot_graph(network_graph: dict):
    '''plots the graph with banwidths between nodes'''
    
    di_graph = DiGraph() 
    data = network_graph
    
    for node_id, node_data in data.items():
        #updating graph to be stored in the json file
        new_id = node_id[2:]
        node_latency = node_data['computing_latency']
        bs_name = node_id
        signal_range = 0
        #node_label = str(new_id) + '\n(' + str(node_latency) + ')'
        node_label = str(new_id)
        node_position = node_data['position']     
        
        new_node = Node(new_id, bs_name, node_label, node_latency, signal_range, signal_range, node_position)
        #pprint(new_node)
        #a = input('')
        di_graph.nodes_set[new_id] = new_node
        
        
        #updating the graph to be drawn
        x_pos = node_position[0]
        y_pos = node_position[1]
        
        di_graph.graph.add_node(node_label,pos=(x_pos, y_pos))
        node_position_aux = np.array(node_position, dtype=np.float32)
        di_graph.graph_positions[node_label] = node_position_aux
    
    #'''
    excluded_keys = ['computing_latency', 'position', 'edges', 'edge_net_latencies', 'edge_net_throughputs']
    for node_id, node_data in data.items():
        src_id = node_id[2:]
        src_name = di_graph.nodes_set[src_id].node_label
        
        for dst, edge_data in node_data.items():
            
            if dst not in excluded_keys:
                dst_id = dst[2:]
                dst_name = di_graph.nodes_set[dst_id].node_label
                #print(dst_name)
                #a = input('')
                
                allocated_bandwidth = edge_data['allocated_bandwidth']
                available_bandwidth = edge_data['available_bandwidth']
                network_throughput = edge_data['network_throughput']
                
                #print(f'\nsrc: {src_name} ({type(src_name)}) -> dst: {dst_name}( {type(dst_name)})')
                #a = input('')
                
                # updating source throughput and latency accordingly
                di_graph.graph.add_edge(
                    u_of_edge=src_name, 
                    v_of_edge=dst_name, 
                    net_available_throughput=available_bandwidth,
                    net_allocated_throughput=allocated_bandwidth,
                    net_throughput=network_throughput
                )
                
                # updating destination throughput and latency accordingly
                di_graph.graph.add_edge(
                    u_of_edge=dst_name, 
                    v_of_edge=src_name, 
                    net_available_throughput=available_bandwidth,
                    net_allocated_throughput=allocated_bandwidth,
                    net_throughput=network_throughput
                )
                
    draw_graph(di_graph, 'any.pdf', throughput=True)


if __name__ == "__main__":
    
    #file variables
    file_dir = './network_topologies/'
    file_name = 'network.json' 
    pdf_name = 'geneve_network.pdf'
    
    
    if os.path.exists('{}{}'.format(file_dir, file_name)):
        print(f'\n*** File {file_name} at {file_dir} already exists! ***')
        print('1- Create a new network topology')
        print('2- Load a network topology')
        option = input('\nEnter your choice: ')
        while option not in ['1', '2']:
            option = input('Enter your choice: ')
        
        if option == '1':
            while True:
                new_file_name = input('\nInform a different network topology name: ')
                if new_file_name != file_name:
                    create_topology(file_dir, new_file_name, pdf_name)
                    break
        else:   
            print('\nLoading network topology...')
            load_topology(file_dir, file_name, pdf_name)
    else:
        create_topology(file_dir, file_name, pdf_name)