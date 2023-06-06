import typing
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.mec import Mec
    from models.base_station import BaseStation
    from models.video import VideoServer
    
from models.hmd import VrHMD 
from models.hmd import VrService 
from models.hmd import Quota
from models.bitrates import BitRateProfiles

""" controller modules """
from controllers import bs_controller 
from controllers import mec_controller 
#from controllers import onos_controller 
from controllers import json_controller 
from controllers import config_controller
#from controllers import server_controller
from controllers import network_controller

""" other modules """
import uuid
import random
import numpy as np
from typing import Dict
from pprint import pprint as pprint

network_controller = network_controller.NetworkController()
bitrate_profiles = BitRateProfiles()

class HmdController:
    """ represents a Vr controller """
    
    @staticmethod
    def __generate_hmd_latency():
        """generates the VrHMD latency based on the file configuration"""
        
        CONFIG = config_controller.ConfigController.get_config()
        lower_latency_threshold = CONFIG['HMDS']['LOWER_LATENCY_THRESHOLD']
        upper_latency_threshold = CONFIG['HMDS']['UPPER_LATENCY_THRESHOLD']
        computing_latency = round(random.uniform(lower_latency_threshold, upper_latency_threshold), 2)
        return computing_latency
    
    @staticmethod
    def __generate_hmd_initial_position() -> dict:
        x = np.random.rand()
        y = np.random.rand()
        
        positions = []
        positions.append(x)
        positions.append(y)
        
        return positions

    @staticmethod
    def create_hmds() -> None:
        """creates HMDs and same them into a json file"""
        
        CONFIG = config_controller.ConfigController.get_config()
        
        total_hmds = CONFIG['NETWORK']['HMDS']
        signal_range = CONFIG['NETWORK']['HMD_RANGE']
        service_per_hmd = CONFIG['NETWORK']['SERVICE_PER_HMD']
        
        hmds_set = {
            "hmds_set": {}
        }
        
        for i in range(total_hmds):
            
            #hmd_id = str(uuid.uuid4())
            hmd_id = i
            computing_latency = HmdController.__generate_hmd_latency()
            position = HmdController.__generate_hmd_initial_position()
            
            hmd = VrHMD(
                id=i,
                signal_range=signal_range,
                computing_latency=computing_latency,
                position=position
            )
            
            #pprint(hmd)
            #a = input('')
            
            #initializing mobile services
            #print(service_per_hmd)
            for i in range(service_per_hmd):
                new_service = VrService(is_mobile=True)
                hmd.services_set.append(new_service)
                hmd.services_ids.append(new_service.id)
                
            hmds_set['hmds_set'][hmd_id] = hmd
            
        json_controller.EncoderController.encoding_to_json(hmds_set)
        return
    
    @staticmethod
    def __connect_hmd_to_base_station(hmd: VrHMD, base_stations: Dict[str, 'BaseStation']) -> None:
        """connects a HMD to a base station"""
        
        max_signal_range = -1
        connected_base_station = None
        for bs_id, base_station in base_stations.items():
            distance = np.sqrt((hmd.position[0] - base_station.position[0])**2 + (hmd.position[1] - base_station.position[1])**2) - 0.03
            
            if distance <= base_station.signal_range and base_station.signal_range > max_signal_range:
                max_signal_range = base_station.signal_range
                connected_base_station = bs_id
        
        if connected_base_station is None:
            hmd.current_base_station = hmd.previous_base_station
        
        else:
            hmd.previous_base_station = hmd.current_base_station
            hmd.current_base_station = connected_base_station
        
    
    @staticmethod
    def connect_hmds_to_base_stations(base_stations: Dict[str, 'BaseStation'], hmds: Dict[str, VrHMD]) -> None:
        """connects all HMDs to base stations"""
        for hmd_id, hmd in hmds.items():
            HmdController.__connect_hmd_to_base_station(hmd, base_stations)

   
    
    
    @staticmethod
    def __generate_hmd_position(hmd: VrHMD) -> dict:
        direction = np.random.uniform(0, 2*np.pi)
        dx = np.cos(direction) * 0.1
        dy = np.sin(direction) * 0.1
        x = (hmd.position[0] + dx)
        y = (hmd.position[1] + dy)
        
        position = []
        position.append(x)
        position.append(y)
        
        return position
    

    @staticmethod
    def update_hmd_positions(base_stations: Dict[str, 'BaseStation'], hmds: Dict[str, VrHMD]) -> None:
        for hmd_id, hmd in hmds.items():
            new_position = HmdController.__generate_hmd_position(hmd)
            new_x = new_position[0]
            new_y = new_position[1]
            
            if new_x < 0 or new_x > 1:
                pass
            else:
                hmd.position[0] = new_x
            
            if new_y < 0 or new_y > 1:
                pass
            else:
                hmd.position[1] = new_y
                
            HmdController.__connect_hmd_to_base_station(hmd, base_stations)

    
    
    @staticmethod 
    def get_vr_service(
        hmds_set: Dict[str, VrHMD], hmd_ip: str, service_id: str
    ) -> dict:
        """gets a vr service """
        
        for service in hmds_set[hmd_ip].services_set:
            if service.id == service_id:
                return service
        
        return None

    @staticmethod 
    def get_vr_service_owner(hmds_set: Dict[str, VrHMD], service: VrService) -> Dict[str, VrHMD]:
        """gets the VrHMD that owns the service"""
        
        hmd_dict: Dict[str, VrHMD] = {
            'id': None,
            'hmd': None
        }
        
        for id, hmd in hmds_set.items():
            for service_id in hmd.services_ids:
                if service_id == service.id:
                    hmd_dict.update({'id': id, 'hmd': hmd})
                    break

        return hmd_dict

    @staticmethod
    def get_hmd(hmds_set: Dict[str, VrHMD], hmd_ip: str) -> VrHMD:
        """gets a VrHMD"""
                
        return hmds_set[hmd_ip]

    @staticmethod
    def remove_vr_service(hmd: VrHMD, service_id: str) -> VrService:
        """ removes a service from where it is deployed """
        
        service_index = [vr_service.id for vr_service in hmd.services_set].index(service_id)
        extracted_service = hmd.services_set.pop(service_index)
        
        return extracted_service

    @staticmethod
    def deploy_vr_service(
        hmds_set: Dict[str, VrHMD], hmd_ip: str, service: VrService
    ) -> None:
        """deployes a VrService into a VrHMD"""
        
        hmds_set[hmd_ip].services_set.append(service)
        return

    @staticmethod 
    def get_hmd_latency(base_station_set: Dict[str,'BaseStation'], vr_hmd: VrHMD) -> float:
        """ gets hmd latency, including the wireless latency where the hmd is connected to """
        
        bs_location = bs_controller.BaseStationController.get_base_station(
            base_station_set, vr_hmd.current_location
        )
        
        hmd_latency = round(bs_location.wireless_latency + vr_hmd.computing_latency, 2) 
        return hmd_latency
        
    @staticmethod
    def switch_quota(service: VrService) -> None:
        """randomly changes a vr service quota """
        #print(f'\nswitching quota for service {service.id}\n')
        quotas_set = Quota.get_quotas_set()
        
        """
        choice options to decide whether to change the quota workload or not:
        -1: previous quota from quota_set
         0: nothing changes
         1: next quota from quota_set
        """
        choice = random.randint(-1, 1)
        if choice!= 0:
            quota_name = service.quota.name
            """ gets quota position """
            position = quotas_set.index(quota_name)

            if choice == -1:
                if position == 0: 
                    """ 
                    can't get the previous quota, because we hitted the first one, then 
                    we go further and get the next quota instead of the previous one 
                    """
                    position = 1
                else:
                    """ otherwise we just get the previous quota position"""
                    position -=1
            else:
                """ 
                can't get the next quota, because we hitted the last one, 
                instead we go back and get the previous quota  
                """
                if position == len(quotas_set) - 1:
                    position -=1
                else:
                    """ otherwise we just get the next quota position """
                    position +=1

            new_quota_name = quotas_set[position]
            service.quota.set_quota(new_quota_name)
        
        return        

    
    '''
    @staticmethod
    def update_hmd_position(hmds_set: Dict[str, VrHMD], hmd_ip: str, new_location: str) -> None:
        """updates the current and previous hmds location"""
        
        hmds_set[hmd_ip].previous_location = hmds_set[hmd_ip].current_location
        hmds_set[hmd_ip].current_location = new_location
        return
                
    @staticmethod
    def update_hmds_positions(hmds_set: Dict[str, VrHMD]) -> None:
        """retrives hosts from ONOS API and updates the location of hmds"""
        
        current_hosts = onos_controller.OnosController.get_hosts()
        
        for host in current_hosts['hosts']:
            hmd_ip = host.ipAddresses[0]
            hmd_location = host.locations[0]['elementId']
            
            HmdController.update_hmd_position(
                hmds_set, hmd_ip, hmd_location
            )
        return
    '''
    staticmethod
    def switch_resolution_based_on_throughput(hmd: VrHMD, manifest: dict, bandwidth: float):
        
        video_versions = sorted(manifest['bitrates'].keys())
        video_version = video_versions[0]
        for version in video_versions:
            if version <= bandwidth:
                video_version = version
            else:
                break        
        
        frame_rate = manifest['bitrates'][video_version]['frame_rate']
        resolution = manifest['bitrates'][video_version]['resolution']
        
        quota_name = bitrate_profiles.get_bitrate_quota_by_throughput(video_version)
        hmd.video_client.refresh_rate = frame_rate
        hmd.video_client.video_quality = resolution
        
        for service in hmd.services_set:
            service.quota.set_quota(quota_name)
        
        #print(f'throughput {bandwidth} | resolution {resolution} | frame rate {frame_rate} | quota: {quota_name}')
        
    
    #TODO: this method should also consider the bitrate profile to analyze both latency and throughput in order to select the best resolution
    def switch_service_video_resolution(
        mec_set: Dict[str,'Mec'], hmds_set: Dict[str, VrHMD], service_owner_ip: str, service_id: str, service_e2e_latency: float
    ) -> None: 
        """changes the video resolution of a service based on its e2e latency"""
        
        CONFIG = config_controller.ConfigController.get_config()
        
        resolution_type = None
        
        resolution_thresholds = {
            '8k': CONFIG['SERVICES']['VIDEO_RESOLUTION']['LATENCY_THRESOLDS']['8k'],
            '4k': CONFIG['SERVICES']['VIDEO_RESOLUTION']['LATENCY_THRESOLDS']['4k'],
            '2k': CONFIG['SERVICES']['VIDEO_RESOLUTION']['LATENCY_THRESOLDS']['2k'],
        }
        
        
        if service_e2e_latency <= resolution_thresholds['8k']:
            resolution_type = '8k'
        elif service_e2e_latency <= resolution_thresholds['4k']:
            resolution_type = '4k'
        elif service_e2e_latency <= resolution_thresholds['2k']:
            resolution_type = '1440p'
        else:
            resolution_type = '1080p'
        
        service: VrService = None
        
        service = HmdController.get_vr_service(hmds_set, service_owner_ip, service_id)
        
        if not service:
            service = mec_controller.MecController.get_mec_service(mec_set, service_id)
        
        service.video_decoder.set_energy_consumption(resolution_type)
        
        
    ######################################################################

    
    '''
    @staticmethod
    def switch_resolution(servers_set: Dict[str, VideoServer], video_id: str):
        """
        1. get or receive the latency
        2. select the resolution according to the bitrate profile
        3. change the video resolution
        """
        resolution_name = '1080p'
        video: 'Video' = ServerController.get_video(servers_set, video_id)
        video.resolution.set_resolution(resolution_name)
    '''
    
    @staticmethod
    def request_manifest(mec_set: Dict[str, 'Mec'], video_id: str):
        #print(f'client requested manifest for video {video_id}')
        return mec_controller.MecController.get_manifest(
            mec_set, video_id
        )
    
    #TODO: check this method
    @staticmethod
    def request_segment(mec_set: Dict[str, 'Mec'], video_id: str, segment_id: int):
        return mec_controller.MecController.get_segment(
            mec_set, video_id, segment_id
        )
    
    
    
    @staticmethod
    def print_hmds(hmds_set: Dict[str, VrHMD]):
        print(f'\nHMDs: {len(hmds_set)}\n')
        for key, values in hmds_set.items():
            pprint(values)
        
    
    
    '''@staticmethod
    def print_clients(clients_set: dict):
        print(f'\nClients: {len(clients_set)}\n')
        for key, values in clients_set.items():
            print(values)
            
    @staticmethod
    def get_clients_keys(clients_set: dict):
        key_list = []
        for key in clients_set.keys():
            key_list.append(key)
        
        return key_list'''