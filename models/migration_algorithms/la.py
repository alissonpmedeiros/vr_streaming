import typing
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.mec import Mec 
    from models.hmd import VrHMD 
    from models.graph import Graph 
    from models.hmd import VrService 
    from models.base_station import BaseStation 
    
from models.migration_ABC import Migration

""" controller modules """
from controllers import hmd_controller 
from controllers import bs_controller 
#from controllers import scg_controller 
from controllers import mec_controller
from controllers import dijkstra_controller 

"""other modules"""
import sys
from typing import Dict
from pprint import pprint as pprint

class LA(Migration):
    """provides a network latency aware (LA) service migration algorithm that considers the resources of the MECs before performing migrations"""
    
    def get_migrations(self):
        return super().get_migrations()
    
    def check_services(
        self, 
        base_station_set: Dict[str,'BaseStation'], 
        mec_set: Dict[str,'Mec'], 
        hmds_set: Dict[str,'VrHMD'], 
        graph: 'Graph'
    ) -> None:
        return super().check_services(
            base_station_set, mec_set, hmds_set, graph
        )

    def service_migration(
        self, 
        base_station_set: Dict[str,'BaseStation'], 
        mec_set: Dict[str,'Mec'], 
        hmds_set: Dict[str,'VrHMD'], 
        graph: 'Graph', 
        service: 'VrService'
    ) -> bool:
        return self.perform_migration(
            base_station_set, mec_set, hmds_set, graph, service
        )
        
    def discover_mec( 
        self, 
        base_station_set: Dict[str,'BaseStation'], 
        mec_set: Dict[str,'Mec'], 
        graph: 'Graph', 
        start_node: 'BaseStation', 
        service: 'VrService'
    ) -> Dict[str,'Mec']:
        """ discovers a nearby MEC server to either offload or migrate the service not considering the resource availaiblity of MEC nodes"""
        
        mec_dict: Dict[str,'Mec'] = {
            'id': None,
            'mec': None
        }
        
        shortest_path = dijkstra_controller.DijkstraController.get_all_E2E_shortest_paths(
            graph, start_node
        )
        
        for node in shortest_path:    
            
            bs_id = node[0][2:]
            base_station: BaseStation = base_station_set[bs_id]
            bs_mec: Mec = mec_set[base_station.mec_id]
            
            if mec_controller.MecController.check_deployment(bs_mec, service):
                mec_dict.update({'id': base_station.mec_id, 'mec': bs_mec})
            break
        
        if not mec_dict.get('mec'):
            print(f'\nALL MEC servers are overloaded! Discarting...')
            a = input('')
        
        return mec_dict

    def perform_migration(
        self, 
        base_station_set: Dict[str,'BaseStation'], 
        mec_set: Dict[str,'Mec'], 
        hmds_set: Dict[str,'VrHMD'], 
        graph: 'Graph', 
        service: 'VrService'
    ) -> bool:
        """
        provides the service migration of service i, which is based on the
        current distance between hmd_ip and where the service is deployed
        """
        
        service_owner: Dict[str, 'VrHMD'] = hmd_controller.HmdController.get_vr_service_owner(
            hmds_set, service
        )
        
        service_owner_hmd: 'VrHMD' = service_owner.get('hmd')
        
        start_node: 'BaseStation' = service_owner_hmd.current_base_station
        
        service_mec_server: 'BaseStation' = None
        if service_owner_hmd.service_offloading:        
            service_mec_server = service_owner_hmd.offloaded_server
            
        print(f'\nbefore migration:\n ')
        print(f'\nservice mec server:')
        pprint(service_mec_server)
        print(f'\nstart node:')
        pprint(start_node)
        
        a = input('')
        
        dst_node: Dict[str, 'Mec'] = self.discover_mec(
            base_station_set, 
            mec_set, 
            graph, 
            start_node, 
            service,
        )
        
        mec_candidate_id: int = dst_node.get('id')
        base_station_candidate = base_station_set[mec_candidate_id]
        mec_candidate: 'Mec' = dst_node.get('mec')
        
        if mec_candidate and service_mec_server:
            
            current_latency: dict = dijkstra_controller.DijkstraController.get_ETE_shortest_path(
                mec_set, graph, start_node, service_mec_server
            )
        
            current_service_latency = current_latency.get('e2e_latency')
            
            extracted_service = mec_controller.MecController.remove_service(
                service_mec_server, service
            )
        
            candidate_latency = dijkstra_controller.DijkstraController.get_ETE_shortest_path(
                mec_set, graph, start_node, base_station_candidate
            )

            candidate_service_latency = candidate_latency.get('e2e_latency')
            
            print('\n hmd connected to base station: ', start_node.id)
            print(f'\nCurrent service latency: {current_service_latency} at MEC {service_mec_server.id}')
            print(f'\nCandidate service latency: {candidate_service_latency} at MEC {mec_candidate_id}')
            
            a = input('')
            
            if current_service_latency > candidate_service_latency:
                mec_controller.MecController.deploy_service(
                    mec_candidate, extracted_service
                )
                self.successful_migrations += 1
                return True
            
            mec_controller.MecController.deploy_service(
                service_mec_server, extracted_service
            )
            self.unsuccessful_migrations += 1
            return False
        else:
            self.unsuccessful_migrations += 1
            return False

            
    
        #if mec_candidate_id or mec_candidate is None:
        #    self.unsuccessful_migrations +=1
        #    return False