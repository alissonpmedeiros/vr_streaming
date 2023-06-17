import typing

if typing.TYPE_CHECKING:
    """ model modules"""
    from models.hmd import VrHMD
    from models.base_station import BaseStation 
    from models.graph import Graph


from controllers import dijkstra_controller
from models.bitrates import BitRateProfiles
from utils.network import generate_networks 

bitrate_profiles = BitRateProfiles()


""" other modules """
import time
import numpy as random
from typing import Dict
from itertools import tee
import matplotlib.pyplot as plt
from pprint import pprint as pprint

MIN_VALUE = -10**9
MIN_THROUGHPUT = 10
MAX_THROUGHPUT = 250
LOGS = True

class NetworkController:
    
    @staticmethod
    def __pairwise(iterable):
        src, dst = tee(iterable)
        next(dst, None)
        return zip(src, dst)

    
    @staticmethod
    def deallocate_bandwidth(graph: 'Graph', route_set: dict, flow_id: int, src_id: str):
                
        path = route_set[src_id][flow_id]['route']
        current_route_bandwidth = route_set[src_id][flow_id]['total_route_bandwidth']
        
        for src, dst in NetworkController.__pairwise(path):
            current_allocated_bandwidth = graph.graph[src][dst]['allocated_bandwidth']
            current_available_bandwidth = graph.graph[src][dst]['available_bandwidth']
            
            new_allocated_bandwidth = round(current_allocated_bandwidth - current_route_bandwidth, 2)
            new_available_bandwidth = round(current_available_bandwidth + current_route_bandwidth, 2)
            
            #updating the allocated and available banwidth from src -> dst
            graph.graph[src][dst]['allocated_bandwidth'] = new_allocated_bandwidth
            graph.graph[src][dst]['available_bandwidth'] = new_available_bandwidth
            
            #updating the allocated and available banwidth from dst -> src
            graph.graph[dst][src]['allocated_bandwidth'] = new_allocated_bandwidth
            graph.graph[dst][src]['available_bandwidth'] = new_available_bandwidth
            
            if new_allocated_bandwidth < 0 or new_available_bandwidth < 0:
                print(f'\n__________________________________________________________\n')
                print(f'CRASHED IN DEALLOCATE_BANDWIDTH!')
                print(f'\nfrom {src} -> {dst}')
                print(f'\nprevious allocated bandwidth: {current_allocated_bandwidth} Mbps')
                print(f'previous available bandwidth: {current_available_bandwidth} Mbps')
                print(f'new allocated bandwidth: {new_allocated_bandwidth} Mbps')
                print(f'new available bandwidth: {new_available_bandwidth} Mbps')
                print(f'\ncurrent route bandwidth: {route_set[src_id][flow_id]["total_route_bandwidth"]} Mbps')
                a = input('')
            
            if LOGS:
                '''
                print(f'\nfrom {src} -> {dst}')
                print(f'\nprevious allocated bandwidth: {current_allocated_bandwidth} Mbps')
                print(f'previous available bandwidth: {current_available_bandwidth} Mbps')
                print(f'new allocated bandwidth: {new_allocated_bandwidth} Mbps')
                print(f'new available bandwidth: {new_available_bandwidth} Mbps')
                print(f'\ncurrent route bandwidth: {route_set[src_id][flow_id]["total_route_bandwidth"]} Mbps')
                '''
                
        
            

        route_set[src_id][flow_id]['total_route_bandwidth'] = 0
        if LOGS:
            pass
            #print(f'\nsucessfully deallocated bandwidth: {current_route_bandwidth} Mbps')
            #print(f'\nnew route bandwidth: {route_set[src_id][flow_id]["total_route_bandwidth"]} Mbps')
        
    
    @staticmethod
    def decrease_bandwidth_reservation(
        graph: 'Graph', route_set: dict, flow_id: int, route: list, decreased_throughput: float
    ):
        if LOGS:
            print(f'\nDecreasing {decreased_throughput} Mbps for route:')
            #print(" -> ".join(route))
        source_node_id = route[0]
        
        if LOGS:
            pass
            #print(f'\ndecreasing {decreased_throughput} from  each pair of nodes in the route...')
        
        for src, dst in NetworkController.__pairwise(route):
    
            current_allocated_bandwidth = graph.graph[src][dst]['allocated_bandwidth']
            current_available_bandwidth = graph.graph[src][dst]['available_bandwidth']
        
            new_allocated_bandwidth = current_allocated_bandwidth - decreased_throughput
            new_available_bandwidth = current_available_bandwidth +  decreased_throughput
          
    
            if new_available_bandwidth < 0 or new_allocated_bandwidth < 0:
                print(f'\n__________________________________________________________\n')
                print(f'\nfrom {src} -> {dst}')
                print(f'current allocated bandwidth: {current_allocated_bandwidth} Mbps')
                print(f'new allocated bandwidth: {new_allocated_bandwidth} Mbps\n')
                print(f'current available bandwidth: {current_available_bandwidth} Mbps')
                print(f'new available bandwidth: {new_available_bandwidth} Mbps')
                print('\n***CRASHED in decrease_bandwidth_reservation!***')
                print(f'printing graph...')    
                while True:
                    generate_networks.plot_graph(graph.graph)
                    time.sleep(10)
            
            if LOGS:
                '''
                print(f'\nfrom {src} -> {dst}')
                print(f'current allocated bandwidth: {current_allocated_bandwidth} Mbps')
                print(f'new allocated bandwidth: {new_allocated_bandwidth} Mbps')
                print(f'current available bandwidth: {current_available_bandwidth} Mbps')
                print(f'new available bandwidth: {new_available_bandwidth} Mbps')
                '''
                
            
            #updating the allocated and available banwidth from src -> dst
            graph.graph[src][dst]['allocated_bandwidth'] = new_allocated_bandwidth
            graph.graph[src][dst]['available_bandwidth'] = new_available_bandwidth
            
            #updating the allocated and available banwidth from dst -> src
            graph.graph[dst][src]['allocated_bandwidth'] = new_allocated_bandwidth
            graph.graph[dst][src]['available_bandwidth'] = new_available_bandwidth
            
        if LOGS:
            pass
            #print(f'\nsource node: {source_node_id}')
            #print(f'\nprevious route bandwidth: {route_set[source_node_id][flow_id]["total_route_bandwidth"]} Mbps')
        route_set[source_node_id][flow_id]['total_route_bandwidth'] -= decreased_throughput
        if LOGS:
            pass
            #print(f'\nnew route bandwidth: {route_set[source_node_id][flow_id]["total_route_bandwidth"]} Mbps')
            #a = input('')
        
    
    @staticmethod
    def increase_bandwidth_reservation(
        graph: 'Graph', route_set: dict, flow_id: int, new_route: list, required_throughput: float
    ):
        if LOGS:
            #print(f'\nIncreasing BW reservation to {required_throughput} Mbps for route:')
            #print(" -> ".join(new_route))
            pass
        src_id = new_route[0]

        if LOGS:
            pass
            #print(f'\nincreasing each pair of nodes in the route...')
        
        for src, dst in NetworkController.__pairwise(new_route):
            
            #a = input('')
            current_allocated_bandwidth = graph.graph[src][dst]['allocated_bandwidth']
            current_available_bandwidth = graph.graph[src][dst]['available_bandwidth']
        
            new_allocated_bandwidth = round(current_allocated_bandwidth + required_throughput, 2)
            new_available_bandwidth = round(current_available_bandwidth - required_throughput, 2)
            
            if LOGS:
                '''
                print(f'\nfrom {src} -> {dst}')
                print(f'previous allocated bandwidth: {current_allocated_bandwidth} Mbps')
                print(f'previous available bandwidth: {current_available_bandwidth} Mbps')
                print(f'new allocated bandwidth: {new_allocated_bandwidth} Mbps')
                print(f'new available bandwidth: {new_available_bandwidth} Mbps')
                '''
            
    
            if new_available_bandwidth < 0:
                print(f'\nfrom {src} -> {dst}')
                print(f'previous allocated bandwidth: {current_allocated_bandwidth} Mbps')
                print(f'previous available bandwidth: {current_available_bandwidth} Mbps')
                print(f'new allocated bandwidth: {new_allocated_bandwidth} Mbps')
                print(f'new available bandwidth: {new_available_bandwidth} Mbps')
                
                print(f'printing graph...')    
                generate_networks.plot_graph(graph.graph)
                a = input('\n***CRASHED in increase_bandwidth_reservation!***')
                return
            #a = input(f'\ntype to get the next pair\n')
            
            #updating the allocated and available banwidth from src -> dst
            graph.graph[src][dst]['allocated_bandwidth'] = new_allocated_bandwidth
            graph.graph[src][dst]['available_bandwidth'] = new_available_bandwidth
            
            #updating the allocated and available banwidth from dst -> src
            graph.graph[dst][src]['allocated_bandwidth'] = new_allocated_bandwidth
            graph.graph[dst][src]['available_bandwidth'] = new_available_bandwidth
            
            #print(f'\nfrom {src} -> {dst}\n\n')
            #pprint(graph.graph[src][dst])
        
        if LOGS:   
            pass
            #print(f'\nprevious route bandwidth: {route_set[src_id][flow_id]["total_route_bandwidth"]} Mbps')
        
        route_set[src_id][flow_id]['total_route_bandwidth'] += required_throughput
        
        if LOGS:
            pass
            #print(f'new route bandwidth: {route_set[src_id][flow_id]["total_route_bandwidth"]} Mbps')
    
    
    @staticmethod
    def route_congested(graph: 'Graph', route: list, required_throughput: float) -> bool:
        congested = False
        for src, dst in NetworkController.__pairwise(route):
            current_available_bandwidth = graph.graph[src][dst]['available_bandwidth']
            if current_available_bandwidth < required_throughput:
                congested = True
                break
        return congested
    
    
    @staticmethod
    def check_served_flows(served_flows, route_set):
        print(f'\n*** checking served flows! ***\n')
        for flow_id in served_flows:
            g = False
            for bs, values in route_set.items():
                if flow_id in values.keys():
                    print(f'current served flow {flow_id} is deployed on: {bs}')
                    g = True
                    break
                    #print(f'route: {values[served_flow]["route"]}')
                    #print(f'total route bandwidth: {values[served_flow]["total_route_bandwidth"]} Mbps')
                    #a = input('')
            if not g:
                print(f'\n***current served flow {flow_id} not found in route_set***\n')
        print(f'\n')
                
    @staticmethod
    def check_served_flow(served_flows, route_set, flow_id):
        #print(f'\nchecking if {flow_id} is in route_set\n')
        for bs, values in route_set.items():
            if flow_id in values.keys():
                print(f'\ncurrent served flow {flow_id} is deployed on: {bs}\n')
                return True
                
        print(f'\n***current served flow {flow_id} NOT found in route_set***\n')
        return False
    
    @staticmethod
    def decrease_all_flow_resolutions(graph: 'Graph', hmds_set: 'VrHMD', route_set: dict, flow_set: dict, served_flows: list):
        #TODO: instead of decreasing all flow resolutions, we must look for all routes passing through the congested node and decrease the bandwidth of all routes passing through that node untill it satisfies at least one quota before the current quota.
        #TODO: after shifting all flow resolutions, we have to consider the current allocated throughput after the first iteration of this function. Consider also dealocating the route...
        
        if LOGS:
            print(f'\n*** DECREASING ALL FLOW RESOLUTIONS ***')
            print(f'served flows: {served_flows}')
            if not served_flows:
                print(f'\nserved flow is empty!')
                a = input('type to continue')
        
        for served_flow in served_flows:
            if LOGS:
                print(f'\n*************************************************************')
                print(f'\n*** served flow: {served_flow} ***')
            
            # HERE WE HAVE TO GET THE SRC AND DST BST AND NOT THE IDS IN THE FLOW...
            flow = flow_set[served_flow]
            src_id = flow['client']
            #dst_id = flow['server']
            
            #TODO: to be undone
            source_node_id = 'BS' + str(hmds_set[str(src_id)].current_base_station)
            #previous_source_node_id = 'BS' + str(hmds_set[str(src_id)].previous_base_station)
            
            '''
            if source_node_id not in route_set.keys():
                print(f'source node: {source_node_id}')
                print(f'key {source_node_id} not found in route_set')
                print(f'route_set keys: {route_set.keys()}')
                a = input('')
            
            
            NetworkController.check_served_flows(served_flows, route_set)
            a = input('type to continue')
            
            
            got = False
            
            for bs, values in route_set.items():
                if served_flow in values.keys():
                    print(f'\ncurrent served flow {served_flow} is deployed on: {bs}')
                    got = True
                    break
                    #print(f'route: {values[served_flow]["route"]}')
                    #print(f'total route bandwidth: {values[served_flow]["total_route_bandwidth"]} Mbps')
                    #a = input('')
            
            if not got:
                print(f'\n current served flow not found in route_set')
                a = input('')
            '''
            
            print(f'\nsource node: {source_node_id}')
            
            
            '''
            if previous_source_node_id != 'BS':
                print(f'\nprevious source node bs: {previous_source_node_id}')
                print(f'\nprevious route set')
                pprint(route_set[previous_source_node_id].keys())
            '''
            
            print(f'\ncurrent route set')
            pprint(route_set[source_node_id].keys())
            
            #NetworkController.check_served_flows(served_flows, route_set)
            
            
            current_route = route_set[source_node_id][served_flow]['route']
            
            flow_throughput = flow_set[served_flow]['throughput']
            new_flow_throughput = bitrate_profiles.get_previous_throughput_profile(flow_throughput)
            
            if new_flow_throughput is None:
                if LOGS:
                    print(f'*** Could not decrease the current served flow resolution ***')
                    print(f'Keep using the lowest throughput profile: {flow_throughput}')
        
            else:
                if LOGS:
                    print(f'new flow throughput: {new_flow_throughput} Mbps')
                
                
                #TODO: we should update the hmd resolution here.
        
                #route_set[source_node_id]['total_route_bandwidth'] = new_flow_throughput
                
                #a = input('\ntype to decrease BW and update plot\n')
                
                decreased_throughput = flow_throughput - new_flow_throughput
                
                NetworkController.decrease_bandwidth_reservation(graph, route_set, served_flow, current_route, decreased_throughput)
                
                flow_set[served_flow]['throughput'] = new_flow_throughput
                
                #generate_networks.plot_graph(graph.graph)
            
            if LOGS:
                pass
                #print(f'current flow throughput: {flow_throughput} Mbps')
                #print(f'new served flow throughput: {new_flow_throughput} Mbps')
                #print(" -> ".join(current_route))
            
            #a = input('')
        
        if LOGS:
            print(f'\n*** FINISH DECREASING ALL FLOW RESOLUTIONS ***')
        #a = input('')
        
        
        

        
    @staticmethod
    def allocate_bandwidth(
        graph: 'Graph', hmds_set: Dict[str, 'VrHMD'], route_set: dict, source_node: 'BaseStation', target_node: 'BaseStation', flow_set: dict, served_flows: list, flow_id: int, required_throughput: float
    ):
    
        src_id = source_node.bs_name
        
        new_route = None
        current_route = None
        
        if src_id not in route_set.keys() or flow_id not in route_set[src_id].keys():
            if LOGS:
                print(f'\n*** NEW ROUTE ***')
            
            new_route, route_max_throughput = dijkstra_controller.DijkstraController.get_widest_path(
                graph, source_node, target_node, required_throughput
            )
            
            
            while route_max_throughput == MIN_VALUE:
                
                if LOGS:
                    print(f'\n*** no routes to fulfill {required_throughput} Mbps ***')
                    print(f'*** recalculating a new route ***')
                
                previous_throughput = required_throughput
                required_throughput = bitrate_profiles.get_previous_throughput_profile(required_throughput)
                
                if required_throughput is None:
                    required_throughput = previous_throughput
                    
                #print(f'*** NEW BW PROFILE {required_throughput} ***')
                new_route, route_max_throughput = dijkstra_controller.DijkstraController.get_widest_path(
                    graph, source_node, target_node, required_throughput
                )
                
                if required_throughput == MIN_THROUGHPUT and route_max_throughput == MIN_VALUE:
                    if LOGS:
                        print(f'\nUsing the lowest throughput profile: {required_throughput}')
                    #required_throughput = previous_throughput
                    NetworkController.decrease_all_flow_resolutions(graph, hmds_set, route_set, flow_set, served_flows)
                    
            
                
                #print(f'route_max_throughput: {route_max_throughput}')
            
            if LOGS:
                #print(" -> ".join(new_route))
                pass
            
            '''
            f = []    
            for bs_id, route in route_set.items():
                r_keys = route.keys()
                for r in r_keys:
                    f.append(r)
            
            f.sort()
            served_flows.sort()
            
            print(f)
            print(served_flows)
            '''
           
            
            if src_id not in route_set.keys():
                route_set[src_id] = {
                    flow_id: {
                        'route': new_route,
                        'total_route_bandwidth': 0
                    }
                }
            
            else:
                route_set[src_id][flow_id] = {
                    'route': new_route,
                    'total_route_bandwidth': 0
                }
            
            #print(f'\nroute added!\n')
            
        else:
            if LOGS:
                print(f'\n*** ROUTE DOES NOT EXISTS! *** \n')
                a = input('type to continue')
            '''
            if len(served_flows) == 2:
                print(f'\n\nTESTING DECREASE_ALL_FLOW_RESOLUTIONS\n')
                print(f'\current served flows\n')
                pprint(served_flows)   
                
                print(f'\nprevious flow set\n')
                pprint(flow_set)    
                
                print(f'\nprevious route set\n')
                pprint(route_set)
                
                
                NetworkController.decrease_all_flow_resolutions(graph, hmds_set, route_set, flow_set, served_flows)
                
                print(f'\nnew flow set\n')
                pprint(flow_set)
                
                print(f'\n\nnew route set\n')
                pprint(route_set)
                
                
                #a = input('TYPE ENTER TO CONTINUE')
            '''
            
            current_route = route_set[src_id][flow_id]['route']
            
            if LOGS:
                print(f'\nDEALLOCATING CURRENT ROUTE')
                print(" -> ".join(current_route))
            
            #a = input('type to deallocate BW and update plot\n')
            
            NetworkController.deallocate_bandwidth(
                graph, route_set, flow_id, src_id
            )
            
            #generate_networks.plot_graph(graph.graph)
            if LOGS:
                print(f'\nRECALCULATING A NEW ROUTE')
            
            new_route, route_max_throughput = dijkstra_controller.DijkstraController.get_widest_path(
                graph, source_node, target_node, required_throughput
            )
                        
            while route_max_throughput == MIN_VALUE:
                if LOGS:    
                    print(f'\n*** no routes to fulfill {required_throughput} Mbps ***')
                    print(f'*** recalculating a new route ***')
                
                previous_throughput = required_throughput
                required_throughput = bitrate_profiles.get_previous_throughput_profile(required_throughput)
                
                if required_throughput is None:
                    required_throughput = previous_throughput
                    
                #print(f'*** NEW BW PROFILE {required_throughput} ***')
                new_route, route_max_throughput = dijkstra_controller.DijkstraController.get_widest_path(
                    graph, source_node, target_node, required_throughput
                )
                
                if required_throughput == MIN_THROUGHPUT and route_max_throughput == MIN_VALUE:
                    if LOGS:
                        print(f'\nUsing the lowest throughput profile: {required_throughput}')
                    
                    #required_throughput = previous_throughput
                    NetworkController.decrease_all_flow_resolutions(graph, hmds_set, route_set, flow_set, served_flows)
        
        if LOGS:
            pass                        
            #print(f'current route: {current_route}')
        
        #a = input('\ntype to increase BW and update plot\n')
        '''
        f = []    
        for bs_id, route in route_set.items():
            r_keys = route.keys()
            for r in r_keys:
                f.append(r)
        
        f.sort()
        served_flows.sort()
        
        print(f)
        print(served_flows)
        '''
        
        NetworkController.increase_bandwidth_reservation(graph, route_set, flow_id, new_route, required_throughput)
        
        
        
        
        '''
        graph_src = new_route[0]
        graph_dst = new_route[1]
        graph_throughput = graph.graph[graph_src]#[graph_dst]['allocated_bandwidth']
        
    
        
        equals = required_throughput == route_set[source_node_id]['total_route_bandwidth'] == graph_throughput
        
        if not equals:
            print(f'\n__________________________________________________________\n')
            print(f'\n SRC NODE: {source_node_id}')
            print(f'\n required_throughput: {required_throughput}')
            print(f'\n graph throughput:')
            pprint(graph_throughput)
            print(f'\n route_set throughput: {route_set[source_node_id]["total_route_bandwidth"]}')
            print(f'\n route:')
            pprint(new_route)        
            a = input('')
        #=sgenerate_networks.plot_graph(graph.graph)
        '''
        
        #if not NetworkController.check_served_flow(served_flows, route_set, flow_id):
        #    a = input('type to continue')
        f = []    
        for bs_id, route in route_set.items():
            r_keys = route.keys()
            for r in r_keys:
                f.append(r)
        
        f.sort()
        served_flows.sort()
        
        print(f)
        print(served_flows)
        
        NetworkController.check_served_flows(served_flows, route_set)
       
        
        #a = input('')
        '''
        '''

        return required_throughput
        
        
        
        
        
        
        
    
        
    
    @staticmethod
    def reset_route(route_set: dict, hmd: 'VrHMD'):
        src_id = hmd.current_base_station
        del route_set[src_id]
    
    @staticmethod
    def check_banwidth_allocation(route_set: dict, hmd: 'VrHMD'):
        ''' calculate a new network throughput based on current network conditions '''
        
        '''
        1. delete current allocated route
        2. recalculate the route and pick up the maximum minumum throughput from widest path
        3. allocated the new route
        '''
        NetworkController.reset_route(route_set, hmd)
        
        
    
    @staticmethod
    def generate_network_plot(base_station_set: Dict[str, 'BaseStation'], hmds_set: Dict[str, 'VrHMD']) -> None:
        plt.xlim(0, 1)
        plt.ylim(0, 1)
        plt.title("Network Graph")
        plt.xlabel("X")
        plt.ylabel("Y")
        
        for base_station in base_station_set.values():
            bs_x_position = base_station.position[0]
            bs_y_position = base_station.position[1]
            circle = plt.Circle((bs_x_position, bs_y_position), base_station.signal_range, color='blue', alpha=0.1)
            plt.gca().add_patch(circle)
            plt.scatter(bs_x_position, bs_y_position, color='blue', marker='o')
            plt.annotate('BS{}'.format(base_station.id), xy=(bs_x_position, bs_y_position), ha='center', va='bottom', color='black')
            
        for hmd_id, hmd in hmds_set.items():
            hmd_x_position = hmd.position[0]
            hmd_y_position = hmd.position[1]
            circle = plt.Circle((hmd_x_position, hmd_y_position), hmd.signal_range, color='red', alpha=0.1)
            #print(circle)
            plt.gca().add_patch(circle)
            plt.scatter(hmd_x_position, hmd_y_position, color='red', marker='x')
            plt.annotate('HMD{}'.format(hmd.id), xy=(hmd_x_position, hmd_y_position), ha='center', va='bottom', color='black')
        '''
        '''
        
        plt.pause(0.01)
        plt.clf()
        
    @staticmethod
    def print_network(base_station_set: Dict[str, 'BaseStation'], hmds_set: Dict[str, 'VrHMD']) -> None:
        plt.figure(figsize=(12, 12))
        while True:
            NetworkController.generate_network_plot(base_station_set, hmds_set)