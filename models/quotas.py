from dataclasses import dataclass, field
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class Quota:
    """ describes the service quotas available in the system"""
    
    name: str = field(default_factory=str, init=True)
    resources: dict = field(default_factory=dict, init=True)

    def __post_init__(self):
        self.resources = self.get_quota(self.name)

    def set_quota(self, name: str):
        self.name = name
        self.resources = self.get_quota(name)

    def get_quota(self, name: str):
        default = "incorrect quota"
        return getattr(self, 'quota_' + str(name), lambda: default)()
    
    def quota_mini(self):
        quota =  { "cpu" : 1, "gpu" : 0}
        return (quota)
    
    def quota_petite(self):
        quota =  { "cpu" : 2, "gpu" : 0}
        return (quota)
    
    def quota_tiny(self):
        quota =  { "cpu" : 4, "gpu" : 0}
        return (quota)
    
    def quota_compact(self):
        quota =  { "cpu" : 6, "gpu" : 0}
        return (quota)
    
    def quota_small(self):
        quota =  { "cpu" : 8, "gpu" : 0}
        return (quota)
    
    def quota_modest(self):
        quota =  { "cpu" : 1, "gpu" : 1}
        return (quota)
    
    def quota_limited(self):
        quota =  { "cpu" : 2, "gpu" : 1}
        return (quota)
    
    def quota_regular(self):
        quota =  { "cpu" : 2, "gpu" : 2}
        return (quota)
    
    def quota_average(self):
        quota =  { "cpu" : 4, "gpu" : 1}
        return (quota)
    
    def quota_medium(self):
        quota =  { "cpu" : 4, "gpu" :2}
        return (quota)  

    def quota_standard(self):
        quota =  { "cpu" : 4, "gpu" : 4}
        return (quota)

    def quota_generous(self):
        quota =  { "cpu" : 6, "gpu" : 1}
        return (quota)
    
    def quota_large(self):
        quota = { "cpu" : 6, "gpu" : 2}
        return (quota) 
    
    def quota_substantial(self):
        quota =  { "cpu" : 6, "gpu" : 4}
        return (quota)

    def quota_plentiful(self):
        quota =  { "cpu" : 6, "gpu" : 6}
        return (quota)

    def quota_ample(self):
        quota =  { "cpu" : 8, "gpu" : 2}
        return (quota)

    def quota_extensive(self):
        quota =  { "cpu" : 8, "gpu" : 4}
        return (quota)

    def quota_huge(self):
        quota =  { "cpu" : 8, "gpu" : 6}
        return (quota)
    
    def quota_massive(self):
        quota =  { "cpu" : 8, "gpu" : 8}
        return (quota)
    
    def quota_grant(self):
        quota =  { "cpu" : 10, "gpu" : 2}
        return (quota)
    
    def quota_giant(self):
        quota =  { "cpu" : 10, "gpu" : 4}
        return (quota)
    
    def quota_king(self):
        quota =  { "cpu" : 10, "gpu" : 6}
        return (quota)
    
    def quota_jumbo(self):
        quota =  { "cpu" : 10, "gpu" : 8}
        return (quota)
    
    def quota_xlarge(self):
        quota = { "cpu" : 10, "gpu" : 10}
        return (quota)
    
    @staticmethod
    def get_quotas_set():
        quotas_set = ['mini', 'petite', 'tiny', 'compact', 'small', 'modest', 'limited', 'regular', 'average', 'medium', 'standard', 'generous', 'large', 'substantial', 'plentiful', 'ample', 'extensive', 'huge', 'massive', 'grant', 'giant', 'king', 'jumbo', 'xlarge']
        return quotas_set