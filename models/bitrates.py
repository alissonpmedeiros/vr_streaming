# https://support.google.com/youtube/answer/1722171?hl=en#zippy=%2Cbitrate        
MAX_THROUGHPUT = 300


class BitRateProfiles:
    
    # Regular network throughput bitrate profiles
    @staticmethod
    def get_throughput_profiles():
        """ generates the throughput profiles for the regular bitrate profiles """
        
        throughput_profiles = {
            25: {'frame_rate': 30, 'latency': 30},
            33: {'frame_rate': 42, 'latency': 26},
            41: {'frame_rate': 54, 'latency': 22},
            50: {'frame_rate': 66, 'latency': 18},
            54: {'frame_rate': 78, 'latency': 18},
            58: {'frame_rate': 90, 'latency': 10},
            63: {'frame_rate': 30, 'latency': 20},
            108: {'frame_rate': 42, 'latency': 18},
            153: {'frame_rate': 54, 'latency': 16},
            200: {'frame_rate': 66, 'latency': 14},
            246: {'frame_rate': 78, 'latency': 12},
            292: {'frame_rate': 90, 'latency': 10},
            304: {'frame_rate': 60, 'latency': 20},
            701: {'frame_rate': 72, 'latency': 17},
            1062: {'frame_rate': 84, 'latency': 14},
            1424: {'frame_rate': 96, 'latency': 11},
            1745: {'frame_rate': 108, 'latency': 8},
            2066: {'frame_rate': 120, 'latency': 5},
            2388: {'frame_rate': 120, 'latency': 10},
            2736: {'frame_rate': 136, 'latency': 9},
            3084: {'frame_rate': 152, 'latency': 8},
            3432: {'frame_rate': 168, 'latency': 7},
            3805: {'frame_rate': 180, 'latency': 6},
            4153: {'frame_rate': 200, 'latency': 5}
        }


        
        return throughput_profiles

    #####################################################################


    # Regular network throughput bitrate profiles
    @staticmethod
    def get_latency_profiles():
        """ generates the network latency profiles for the regular bitrate profiles """
        
        latency_profiles = {
            30: {'throughput': 25, 'frame_rate': 30},
            26: {'throughput': 33, 'frame_rate': 42},
            22: {'throughput': 41, 'frame_rate': 54},
            18: {'throughput': 50, 'frame_rate': 66},
            18: {'throughput': 54, 'frame_rate': 78},
            10: {'throughput': 58, 'frame_rate': 90},
            20: {'throughput': 63, 'frame_rate': 30},
            18: {'throughput': 108, 'frame_rate': 42},
            16: {'throughput': 153, 'frame_rate': 54},
            14: {'throughput': 200, 'frame_rate': 66},
            12: {'throughput': 246, 'frame_rate': 78},
            10: {'throughput': 292, 'frame_rate': 90},
            20: {'throughput': 304, 'frame_rate': 60},
            17: {'throughput': 701, 'frame_rate': 72},
            14: {'throughput': 1062, 'frame_rate': 84},
            11: {'throughput': 1424, 'frame_rate': 96},
            8: {'throughput': 1745, 'frame_rate': 108},
            5: {'throughput': 2066, 'frame_rate': 120},
            10: {'throughput': 2388, 'frame_rate': 120},
            9: {'throughput': 2736, 'frame_rate': 136},
            8: {'throughput': 3084, 'frame_rate': 152},
            7: {'throughput': 3432, 'frame_rate': 168},
            6: {'throughput': 3805, 'frame_rate': 180},
            5: {'throughput': 4153, 'frame_rate': 200},
        }

        return latency_profiles

    @staticmethod
    def get_bitrate_quota_profiles():
        """maps each quota into a specific bitrate profile"""
        bitrate_quotas = {
            #4k week interaction
            'mini': {'throughput': 25, 'frame_rate': 30, 'latency': 30},
            'petite': {'throughput': 33, 'frame_rate': 42, 'latency': 26},
            'tiny': {'throughput': 41, 'frame_rate': 54, 'latency': 22},
            #4k strong intraction
            'compact': {'throughput': 50, 'frame_rate': 66, 'latency': 18},
            'small': {'throughput': 54, 'frame_rate': 78, 'latency': 18},
            'modest': {'throughput': 58, 'frame_rate': 90, 'latency': 10},
            #8k week interaction
            'limited': {'throughput': 63, 'frame_rate': 30, 'latency': 20},
            'regular': {'throughput': 108, 'frame_rate': 42, 'latency': 18},
            'average': {'throughput': 153, 'frame_rate': 54, 'latency': 16},
            # 8k strong interaction
            'medium': {'throughput': 200, 'frame_rate': 66, 'latency': 14},
            'standard': {'throughput': 246, 'frame_rate': 78, 'latency': 12},
            'generous': {'throughput': 292, 'frame_rate': 90, 'latency': 10},
            #12k week interaction
            'large': {'throughput': 304, 'frame_rate': 60, 'latency': 20},
            'substantial': {'throughput': 701, 'frame_rate': 72, 'latency': 17},
            'plentiful': {'throughput': 1062, 'frame_rate': 84, 'latency': 14},
            #12k strong interaction
            'ample': {'throughput': 1424, 'frame_rate': 96, 'latency': 11},
            'extensive': {'throughput': 1745, 'frame_rate': 108, 'latency': 8},
            'huge': {'throughput': 2066, 'frame_rate': 120, 'latency': 5},
            #24k week interaction
            'massive': {'throughput': 2388, 'frame_rate': 120, 'latency': 10},
            'grant': {'throughput': 2736, 'frame_rate': 136, 'latency': 9},
            'giant': {'throughput': 3084, 'frame_rate': 152, 'latency': 8},
            #24k strong interaction
            'king': {'throughput': 3432, 'frame_rate': 168, 'latency': 7},
            'jumbo': {'throughput': 3805, 'frame_rate': 180, 'latency': 6},
            'xlarge': {'throughput': 4153, 'frame_rate': 200, 'latency': 5},
        }
        
        return bitrate_quotas

    @staticmethod
    def get_bitrate_quota(latency, throughput):
        bitrate_quotas = BitRateProfiles.get_bitrate_quota_profiles()
        
        valid_quotas = {k: v for k, v in bitrate_quotas.items() if v['throughput'] <= throughput}

        # Initialize variables to keep track of the best match found so far
        best_match = None
        best_latency_diff = float('inf')

        # Loop through the valid quotas to find the best match
        for quota_name, quota_values in valid_quotas.items():
            quota_latency = quota_values['latency']

            # Check if the quota's latency is less than or equal to the specified latency
            if quota_latency <= latency:
                # Calculate the difference between the quota's latency and the specified latency
                latency_diff = latency - quota_latency

                # Check if the current quota is a better match based on latency difference
                if latency_diff <= best_latency_diff:
                    best_match = quota_name
                    best_latency_diff = latency_diff
                
        return bitrate_quotas[best_match]


    @staticmethod
    def get_bitrate_quota_by_latency(latency: float) -> str:
        bitrate_quotas = BitRateProfiles.get_bitrate_quota_profiles()
        for quota, profile in bitrate_quotas.items():
            if profile['latency'] == latency:
                return quota
    
    @staticmethod
    def get_bitrate_quota_by_throughput(throughput: float) -> str:
        bitrate_quotas = BitRateProfiles.get_bitrate_quota_profiles()
        for quota, profile in bitrate_quotas.items():
            if profile['throughput'] == throughput:
                return quota
    
    
    @staticmethod
    def get_previous_latency_profile(required_latency: float):
        bitrate_latency_profiles = BitRateProfiles.get_latency_profiles()
        profile_keys = list(bitrate_latency_profiles.keys())
        profile_keys.sort()
        previous_latency = None
        
        for latency in profile_keys:
            if latency >= required_latency:
                return previous_latency
            previous_latency = latency
        return None
    
    @staticmethod
    def get_next_latency_profile(required_latency: float):
        bitrate_latency_profiles = BitRateProfiles.get_latency_profiles()
        profile_keys = list(bitrate_latency_profiles.keys())
        profile_keys.sort()
        
        for latency in profile_keys:
            if latency > required_latency:
                return latency
            
        return required_latency
    
    @staticmethod
    def get_previous_throughput_profile(required_throughput: float):
        bitrate_throughput_profiles = BitRateProfiles.get_throughput_profiles()
        profile_keys = list(bitrate_throughput_profiles.keys())
        profile_keys.sort()
        previous_throughput = None
        
        for throughput in profile_keys:
            if throughput >= required_throughput:
                return previous_throughput
            previous_throughput = throughput
        return None
    
    @staticmethod
    def get_next_throughput_profile(required_throughput: float):
        bitrate_throughput_profiles = BitRateProfiles.get_throughput_profiles()
        profile_keys = list(bitrate_throughput_profiles.keys())
        profile_keys.sort()
        
        for throughput in profile_keys:
            if throughput > required_throughput:
                return throughput
            
        return required_throughput
    
    def __generate_profiles():
        network = 10  
        decoder = 500
        for i in range (25):
            if i%6==0 and i > 4: 
                print(f'\n##############################\n') 
            print(f'\n {network} | {decoder}')
            network += 8    
            decoder += 62.5



        