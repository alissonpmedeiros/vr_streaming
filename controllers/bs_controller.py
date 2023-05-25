#import sys
#from pathlib import Path
#sys.path.append(str(Path('.').absolute().parent))

import typing
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.mec import Mec 

from models.base_station import BaseStation 


""" controller modules """
from controllers import json_controller
from controllers import config_controller

"""other modules"""

from typing import Dict
from pprint import pprint as pprint 


class BaseStationController:
    """ represents a base station controller """
    
    @staticmethod
    def get_base_station(base_station_set: Dict[str, BaseStation], bs_id: str) -> BaseStation:
        """gets a base station by ID"""
        
        return base_station_set[bs_id]
                   
    @staticmethod
    def get_base_station_by_name(base_station_set: Dict[str, BaseStation], bs_name: str) -> Dict[str, BaseStation]:
        """gets the base station by name and returns its ID and its object"""
        
        bs_dict: Dict[str, BaseStation] = {
            'id': None,
            'base_station': None
        }
        
        for bs_id, base_station in base_station_set.items():
            if base_station.bs_name == bs_name:
                bs_dict.update({'id': bs_id, 'base_station': base_station})
                break
        
        return bs_dict
    
    """ 
    @staticmethod
    def print_base_stations(base_station_set: Dict[str, BaseStation]) -> None:
        for bs_id, base_station in base_station_set.items():
            print(f'\nid: {bs_id}')
            print(f'name: {base_station.bs_name}')
            print(f'links:')
            for key, value in base_station.links.items():
                print(f'dst: {key} -> [{value["latency"]}]')   
        return
    """
        
