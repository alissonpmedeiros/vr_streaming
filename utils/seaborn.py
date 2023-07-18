import pandas as pd
from csv_encoder import CSV
from pprint import pprint as pprint


FILE_NAMES = ['bw.csv', 'latency_bw_restriction.csv', 'offloading.csv']
PLOT_DIR = ['1k\\', '2k\\', '3k\\', '4k\\']
RESULTS_DIR = "C:\\Users\\Alisson Cds\\Downloads\\vr_streaming\\results\\"

class DataFrame:
    
    @staticmethod
    def get_df_data(file_dir: str, file_name: str):
        file = '{}{}.csv'.format(file_dir, file_name)
        
        data_frame = pd.read_csv(file)
        return data_frame

if __name__ == "__main__":
    data_frames = []
    for file_name in FILE_NAMES:
        for plot_dir in PLOT_DIR:
            print("{}{}{}".format(RESULTS_DIR, plot_dir, file_name))
            file_dir = "{}{}".format(RESULTS_DIR, plot_dir)
            data_frame = pd.read_csv("{}{}".format(file_dir, file_name))
            algorithm = None,
            scenario = None,
            
            if file_name == 'bw.csv':
                algorithm = 'alg1'
            elif file_name == 'latency_bw_restriction.csv':
                algorithm = 'alg2'
            else:
                algorithm = 'alg3'
            
            if plot_dir == '1k\\':
                scenario = 'scenario 1'
            elif plot_dir == '2k\\':
                scenario = 'scenario 2'
            elif plot_dir == '3k\\':
                scenario = 'scenario 3'
            else:
                scenario = 'scenario 4'
            
            data_frame.insert(0, 'scenario', scenario)
            data_frame.insert(1, 'algorithm', algorithm)
            
            data_frames.append(data_frame)
            
    merged_df = pd.concat(data_frames, ignore_index=True)         
    merged_df.to_csv('merged_file.csv', index=False)