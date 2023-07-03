# https://support.google.com/youtube/answer/1722171?hl=en#zippy=%2Cbitrate        
MAX_THROUGHPUT = 300


class BitRateProfiles:
    
    # Regular network throughput bitrate profiles
    @staticmethod
    def get_throughput_profiles():
        """ generates the throughput profiles for the regular bitrate profiles """
        
        throughput_profiles = {
            # Video Bitrate for 1K (1080p), Standard Frame Rate (24, 25, 30)
            10: {
                'resolution': '1k',
                'frame_rate': 24,
                'network_latency': 56,
                'decoder_latency': 1937.5,
            },
            12: {
                'resolution': '1k',
                'frame_rate': 25,
                'network_latency': 54,
                'decoder_latency': 1875,
            },
            14: {
                'resolution': '1k',
                'frame_rate': 30,
                'network_latency': 52,
                'decoder_latency': 1812.5,
            },
            # Video Bitrate for 1K (1080p), High Frame Rate (48, 50, 60)
            16: {
                'resolution': '1k',
                'frame_rate': 48,
                'network_latency': 50,
                'decoder_latency': 1750,
            },
            18: {
                'resolution': '1k',
                'frame_rate': 50,
                'network_latency': 48,
                'decoder_latency': 1687.5,
            },
            19: {
                'resolution': '1k',
                'frame_rate': 60,
                'network_latency': 46,
                'decoder_latency': 1625,
            },
            # Video Bitrate for 2K (1440p), Standard Frame Rate (24, 25, 30)
            20: {
                'resolution': '2k',
                'frame_rate': 24,
                'network_latency': 44,
                'decoder_latency': 1562.5,
            },
            23: {
                'resolution': '2k',
                'frame_rate': 25,
                'network_latency': 42,
                'decoder_latency': 1500,
            },
            26: {
                'resolution': '2k',
                'frame_rate': 30,
                'network_latency': 40,
                'decoder_latency': 1437.5,
            },
            # Video Bitrate for 2K (1440p), High Frame Rate (48, 50, 60)
            30: {
                'resolution': '2k',
                'frame_rate': 48,
                'network_latency': 38,
                'decoder_latency': 1375,
            },
            33: {
                'resolution': '2k',
                'frame_rate': 50,
                'network_latency': 36,
                'decoder_latency': 1312.5,
            },
            36: {
                'resolution': '2k',
                'frame_rate': 60,
                'network_latency': 34,
                'decoder_latency': 1250,
            },
            # Video Bitrate for 4K, Standard Frame Rate (24, 25, 30)
            44: {
                'resolution': '4k',
                'frame_rate': 24,
                'network_latency': 32,
                'decoder_latency': 1187.5,
            },
            48: {
                'resolution': '4k',
                'frame_rate': 25,
                'network_latency': 30,
                'decoder_latency': 1125,
            },
            52: {
                'resolution': '4k',
                'frame_rate': 30,
                'network_latency': 28,
                'decoder_latency': 1062.5,
            },
            # Video Bitrate for 4K, High Frame Rate (48, 50, 60)
            66: {
                'resolution': '4k',
                'frame_rate': 48,
                'network_latency': 26,
                'decoder_latency': 1000,
            },
            72: {
                'resolution': '4k',
                'frame_rate': 50,
                'network_latency': 24,
                'decoder_latency': 937.5,
            },
            78: {
                'resolution': '4k',
                'frame_rate': 60,
                'network_latency': 22,
                'decoder_latency': 875,
            },
            # Video Bitrate for 8K, Standard Frame Rate (24, 25, 30)
            100: {
                'resolution': '8k',
                'frame_rate': 24,
                'network_latency': 20,
                'decoder_latency': 812.5,
            },
            117: {
                'resolution': '8k',
                'frame_rate': 25,
                'network_latency': 18,
                'decoder_latency': 750,
            },
            134: {
                'resolution': '8k',
                'frame_rate': 30,
                'network_latency': 16,
                'decoder_latency': 687.5,
            },
            # Video Bitrate for 8K, High Frame Rate (48, 50, 60)
            151: {
                'resolution': '8k',
                'frame_rate': 48,
                'network_latency': 14,
                'decoder_latency': 625,
            },
            200: {
                'resolution': '8k',
                'frame_rate': 50,
                'network_latency': 12,
                'decoder_latency': 562.5,
            },
            250: {
                'resolution': '8k',
                'frame_rate': 60,
                'network_latency': 10,
                'decoder_latency': 500,
            }
        }

        
        return throughput_profiles

    #####################################################################


    # Regular network throughput bitrate profiles
    @staticmethod
    def get_latency_profiles():
        """ generates the network latency profiles for the regular bitrate profiles """
        
        latency_profiles = {
            # Video Bitrate for 8K, Standard Frame Rate (24, 25, 30)
            # Video Bitrate for 8K, High Frame Rate (48, 50, 60)
            10: {
            'resolution': '8k',
            'frame_rate': 60,
            'throughput': 250,
            'decoder_latency': 500,
            },
            12: {
            'resolution': '8k',
            'frame_rate': 50,
            'throughput': 200,
            'decoder_latency': 562.5,
            },
            14: {
            'resolution': '8k',
            'frame_rate': 48,
            'throughput': 151,
            'decoder_latency': 625,
            },
            16: {
            'resolution': '8k',
            'frame_rate': 30,
            'throughput': 134,
            'decoder_latency': 687.5,
            },
            18: {
            'resolution': '8k',
            'frame_rate': 25,
            'throughput': 117,
            'decoder_latency': 750,
            },
            20: {
            'resolution': '8k',
            'frame_rate': 24,
            'throughput': 100,
            'decoder_latency': 812.5,
            },
            # Video Bitrate for 4K, High Frame Rate (48, 50, 60)
            22: {
            'resolution': '4k',
            'frame_rate': 60,
            'throughput': 78,
            'decoder_latency': 875,
            },
            24: {
            'resolution': '4k',
            'frame_rate': 50,
            'throughput': 72,
            'decoder_latency': 937.5,
            },
            26: {
            'resolution': '4k',
            'frame_rate': 48,
            'throughput': 66,
            'decoder_latency': 1000,
            },
            # Video Bitrate for 4K, Standard Frame Rate (24, 25, 30)
            28: {
            'resolution': '4k',
            'frame_rate': 25,
            'throughput': 48,
            'decoder_latency': 1125,
            },
            30: {
            'resolution': '4k',
            'frame_rate': 30,
            'throughput': 52,
            'decoder_latency': 1062.5,
            },
            32: {
            'resolution': '4k',
            'frame_rate': 24,
            'throughput': 44,
            'decoder_latency': 1187.5,
            },
            # Video Bitrate for 2K (1440p), High Frame Rate (48, 50, 60)
            34: {
            'resolution': '2k',
            'frame_rate': 60,
            'throughput': 36,
            'decoder_latency': 1250,
            },
            36: {
            'resolution': '2k',
            'frame_rate': 50,
            'throughput': 33,
            'decoder_latency': 1312.5,
            },
            38: {
            'resolution': '2k',
            'frame_rate': 48,
            'throughput': 30,
            'decoder_latency': 1375,
            },
            # Video Bitrate for 2K (1440p), Standard Frame Rate (24, 25, 30)
            40: {
            'resolution': '2k',
            'frame_rate': 30,
            'throughput': 26,
            'decoder_latency': 1437.5,
            },
            42: {
            'resolution': '2k',
            'frame_rate': 25,
            'throughput': 23,
            'decoder_latency': 1500,
            },
            44: {
            'resolution': '2k',
            'frame_rate': 24,
            'throughput': 20,
            'decoder_latency': 1562.5,
            },
            # Video Bitrate for 1K (1080p), High Frame Rate (48, 50, 60)
            46: {
            'resolution': '1k',
            'frame_rate': 60,
            'throughput': 19,
            'decoder_latency': 1625,
            },
            48: {
            'resolution': '1k',
            'frame_rate': 50,
            'throughput': 18,
            'decoder_latency': 1687.5,
            },
            50: {
            'resolution': '1k',
            'frame_rate': 48,
            'throughput': 16,
            'decoder_latency': 1750,
            },
            # Video Bitrate for 1K (1080p), Standard Frame Rate (24, 25, 30)
            52: {
            'resolution': '1k',
            'frame_rate': 30,
            'throughput': 14,
            'decoder_latency': 1812.5,
            },
            54: {
            'resolution': '1k',
            'frame_rate': 25,
            'throughput': 12,
            'decoder_latency': 1875,
            },
            56: {
            'resolution': '1k',
            'frame_rate': 24,
            'throughput': 10,
            'decoder_latency': 1937.5,
            }
        }
        return latency_profiles

    @staticmethod
    def get_bitrate_quota_profiles():
        """maps each quota into a specific bitrate profile"""
        bitrate_quotas = {
            'mini': {'latency': 56, 'throughput': 10},
            'petite': {'latency': 54, 'throughput': 12},
            'tiny': {'latency': 52, 'throughput': 14},
            'compact': {'latency': 50, 'throughput': 16},
            'small': {'latency': 48, 'throughput': 18},
            'modest': {'latency': 46, 'throughput': 19},
            'limited': {'latency': 44, 'throughput': 20},
            'regular': {'latency': 42, 'throughput': 23},
            'average': {'latency': 40, 'throughput': 26},
            'medium': {'latency': 38, 'throughput': 30},
            'standard': {'latency': 36, 'throughput': 33},
            'generous': {'latency': 34, 'throughput': 36},
            'large': {'latency': 32, 'throughput': 44},
            'substantial': {'latency': 30, 'throughput': 48},
            'plentiful': {'latency': 28, 'throughput': 52},
            'ample': {'latency': 26, 'throughput': 66},
            'extensive': {'latency': 24, 'throughput': 72},
            'huge': {'latency': 22, 'throughput': 78},
            'massive': {'latency': 20, 'throughput': 100},
            'grant': {'latency': 18, 'throughput': 117},
            'giant': {'latency': 16, 'throughput': 134},
            'king': {'latency': 14, 'throughput': 151},
            'jumbo': {'latency': 12, 'throughput': 200},
            'xlarge': {'latency': 10, 'throughput': 250}
        }
        
        return bitrate_quotas

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



        