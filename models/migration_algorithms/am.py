import typing
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.mec import Mec 
    from models.vr import VrHMD 
    from models.graph import Graph 
    from models.vr import VrService 
    from models.base_station import BaseStation 

from models.migration_ABC import Migration

""" controller modules """
from controllers import vr_controller 
from controllers import bs_controller 
from controllers import mec_controller 

"""other imports"""
from typing import Dict


class AlwaysMigrate(Migration):
    """ implements the migration behaviour trigered by handover """


    def get_migrations(self) -> dict:
        return super().get_migrations()
    
    def check_services(
        self, base_station_set: Dict[str,'BaseStation'], mec_set: Dict[str,'Mec'], hmds_set: Dict[str,'VrHMD'], graph: 'Graph'
    ) -> None:
        return super().check_services(base_station_set, mec_set, hmds_set, graph)
    
    
    def service_migration(
        self, 
        base_station_set: Dict[str,'BaseStation'], 
        mec_set: Dict[str,'Mec'], 
        hmds_set: Dict[str,'VrHMD'],
        graph: 'Graph',
        service: 'VrService',
     ) -> bool:
        
        service_owner: Dict[str, 'VrHMD'] = vr_controller.VrController.get_vr_service_owner(
            hmds_set, service
        )
    
        service_owner_hmd: 'VrHMD' = service_owner.get('hmd')
        
        return self.perform_migration(
            base_station_set,
            mec_set,
            service_owner_hmd,
            service,
        )
            
    def perform_migration(
        self,
        base_station_set: Dict[str,'BaseStation'],
        mec_set: Dict[str,'Mec'],
        hmd: 'VrHMD',
        service: 'VrService',
    ) -> bool:
        """
        provides the service migration of service i, which is based on the
        current distance between hmd_ip and where the service is deployed. 
        Typically, the always migration method is based on the user handover. 
        Whenever the handover takes place, the service is moved to the nearby MEC server.
        """

        hmd_bs = bs_controller.BaseStationController.get_base_station(
            base_station_set, hmd.current_location
        )
        
        bs_mec = mec_controller.MecController.get_mec(mec_set, hmd_bs)

        if mec_controller.MecController.check_deployment(
            bs_mec, service
        ):
            service_server: Dict[str,'Mec'] = mec_controller.MecController.get_service_mec_server(
                mec_set, service.id
            )
            
            service_mec_server = service_server.get('mec')
            
            if service_mec_server is None:
                self.unsuccessful_migrations += 1
                return False
            
            extracted_service = mec_controller.MecController.remove_service(
                service_mec_server, service
            )
            
            mec_controller.MecController.deploy_service(bs_mec, extracted_service)
            self.successful_migrations += 1
            return True
        else:
            self.unsuccessful_migrations += 1
            return False




    