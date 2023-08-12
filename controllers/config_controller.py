import yaml

class ConfigController:
    @staticmethod
    def get_config():
        """ Gets the configuration file from ~/scg/config.yaml """
        
        CONFIG_FILE = r"/home/medeiros/vr_streaming/config.yaml"
        # CONFIG_FILE = r"/Users/alisson-cds/Desktop/vr_streaming/config.yaml"
        
        with open(CONFIG_FILE, 'r') as file:
            CONFIG = yaml.load(file, Loader=yaml.FullLoader)
            return CONFIG