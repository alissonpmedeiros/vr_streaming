import typing
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.hmd import VrHMD
    from models.base_station import BaseStation



import numpy as np
import matplotlib.pyplot as plt
from models.video import Video
from pprint import pprint as pprint
from controllers import server_controller
from controllers import client_controller



from typing import Dict
    

servers_dict = {
    'servers_set': {}
}

clients_dict = {
    'clients_set': {}
}

servers_set = servers_dict['servers_set']
clients_set = clients_dict['clients_set']

video1 = Video(3, 60)
video2 = Video(10, 60)
video3 = Video(20, 60)

#print(video)

server_controller.ServerController.add_server(servers_set)
server_controller.ServerController.add_server(servers_set)
server_controller.ServerController.add_server(servers_set)

client_controller.ClientController.add_client(clients_set)
client_controller.ClientController.add_client(clients_set)
client_controller.ClientController.add_client(clients_set)


servers_keys = server_controller.ServerController.get_servers_keys(servers_set)
server_controller.ServerController.add_video(servers_set, servers_keys[0], video1)
server_controller.ServerController.add_video(servers_set, servers_keys[1], video2)
server_controller.ServerController.add_video(servers_set, servers_keys[2], video3)

client_keys = client_controller.ClientController.get_clients_keys(clients_set)

#client_controller.ClientController.print_clients(clients_set)

#server_controller.ServerController.print_servers(servers_set)


manifest = client_controller.ClientController.request_manifest(servers_set, video1.id)

pprint(manifest)

'''
server_controller.print_servers(servers_set)
client_controller.print_clients(clients_set)

manifest1 = server_controller.ServerController.get_manifest(servers_set, video1.id)
manifest2 = server_controller.ServerController.get_manifest(servers_set, video2.id)
manifest3 = server_controller.ServerController.get_manifest(servers_set, video3.id)

print(f'\n')
pprint(manifest1)
print(f'\n')
pprint(manifest2)
print(f'\n')
pprint(manifest3)
'''                

def print_network(base_stations: Dict[str, 'BaseStation'], hmds: Dict[str, 'VrHMD']):
    
    #TODO: before testing we need to include plt.figure(figsize=(12, 12)) in the main file
    
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.title("Network Graph")
    plt.xlabel("X")
    plt.ylabel("Y")
    
    for bs_id, base_station in base_stations.items():
        circle = plt.Circle((base_station.x, base_station.y), base_station.signal_range, color='blue', alpha=0.1)
        plt.gca().add_patch(circle)
        plt.scatter(base_station.x, base_station.y, color='blue', marker='o')
        plt.annotate('BS{}'.format(base_station.id), xy=(base_station.x, base_station.y), ha='center', va='bottom', color='black')

    for hmd_id, hmd in hmds.items():
        circle = plt.Circle((hmd.x, hmd.y), hmd.signal_range, color='red', alpha=0.1)
        plt.gca().add_patch(circle)
        plt.scatter(hmd.x, hmd.y, color='red', marker='x')
        plt.annotate('HMD{}'.format(hmd.id), xy=(hmd.x, hmd.y), ha='center', va='bottom', color='black')
    
    plt.pause(0.01)
    plt.clf()