""" other modules """
import statistics, yaml
from typing import Any
import numpy as np
import scipy
import pandas as pd
import seaborn as sns
from empiricaldist import Cdf  # pip install empiricaldist
import matplotlib.pyplot as plt
from pprint import pprint as pprint

""" controller modules """
#from controllers import config_controller as config_controller
from .. controllers import config_controller
from . csv_encoder import CSV
""" other modules """
import os
import textwrap
 

CONFIG = config_controller.ConfigController.get_config()
RESULTS_DIR = CONFIG['SYSTEM']['RESULTS_DIR']
    
class DataFrame:
    
    @staticmethod
    def get_df_data(file_dir: str, file_name: str):
        file = '{}{}.csv'.format(file_dir, file_name)
        
        data_frame = pd.read_csv(file)
        return data_frame
    
    @staticmethod
    def calculate_average(data_frame: Any, kpi: str):
        df_mean = data_frame[[kpi]].mean()
        return round(float(df_mean), 2)
    
    
    @staticmethod
    def calculate_std(data_frame: Any, kpi: str):
        df_std = data_frame[[kpi]].std()
        return round(float(df_std), 2)
    
    

class Results:
    
    @staticmethod
    def read_files(file_dir: str, cities: dict, algorithms: list):
        
        results = {
            'bern':   {},
            'geneva': {},
            'zurich': {}       
        }
        
        for city, radius in cities.items():
            #print(f'\n##################################################')
            #print(f'City of {city}')
            for r in radius: 
                radius_name = 'r_0{}'.format(r)
                #print(f'__________________________________')
                #print(f'\n*** radius: {radius_name} ***')
                radius_dir = '{}/{}/{}/'.format(file_dir, city, radius_name)
                results[city][radius_name] = {}
                for algorithm in algorithms:
                    #print(f'\nalgorithm: {algorithm}')
                    result = DataFrame.get_df_data(radius_dir, algorithm)
                    results[city][radius_name][algorithm] = result
            
            #print(f'\n##################################################\n')
        #print(results)
        #a = input('')
        return results
    
    @staticmethod
    def create_overleaf_topology_directories_(overleaf_dir: str, cities: dict):
        """ creates the directories for each topology into overleaf dir """
        for city, radius in cities.items():
            city_dir = os.path.join(overleaf_dir, city)
            if not os.path.exists(city_dir):
                os.mkdir(city_dir)
                '''
                for r in radius: 
                    radius_name = 'r_0{}'.format(r)
                    radius_dir = os.path.join(city_dir, radius_name)
                    if not os.path.exists(radius_dir):
                        os.mkdir(radius_dir)
                '''
                
       
    @staticmethod
    def get_bar_plot_file_header(energy=False, latency=False):
        global algorithms
        file_header = []
        file_header.append('x')
        for algorithm in algorithms:
            file_header.append(algorithm)
            if energy:
                file_header.append(str(algorithm+'-hmd'))
            elif latency:
                file_header.append(str(algorithm+'-net'))
            
            file_header.append(str(algorithm+'-std'))
        
        return file_header

    @staticmethod
    def get_line_plot_file_header():
        global algorithms
        file_header = []
        file_header.append('x')
        
        for algorithm in algorithms:
            file_header.append(algorithm)
        
        return file_header
    
    @staticmethod
    def get_box_plot_file_header():
        global algorithms
        file_header = []
        
        for algorithm in algorithms:
            file_header.append(algorithm)
        
        return file_header
                
class BarPlot:                
    
    """
    all methods receive a DataFrame and produces a csv file that will be used by overleaf
    """
    
    @staticmethod
    def create_bar_plot(overleaf_dir: str, results: dict, kpi: str):
        """ 
        Can be used by all other KPIs
        1. first row is x, which represents the radius for a specific topology
        2. other rows are specified according to each algorithm 
        3. each algorithm has the following rows: alg-name and alg-std, where for latency and energy plots there are alg-net and alg-hmd fields, respectively
        """
        for city, radius in results.items():
            #print(f'city: {city}')
            city_dir = '{}{}/'.format(overleaf_dir, city)
            file_name = '{}_{}_bar.csv'.format(city, kpi)
            file_headers = None
            if kpi == 'ete_latency':
                file_headers= Results.get_bar_plot_file_header(latency=True)
            elif kpi == 'energy':
                file_headers = Results.get_bar_plot_file_header(energy=True)
            else:
                file_headers = Results.get_bar_plot_file_header()
                
             
            CSV.create_file(city_dir, file_name, file_headers)
            
            x_value = 100
            for radius_id, algorithms in radius.items():
                #print(f'\n\nradius: {radius_id}\n')
                algorithms_performance = []
                algorithms_performance.append(x_value)
                
                for algorithm, alg_data_frame in algorithms.items(): 
                    alg_avg = DataFrame.calculate_average(alg_data_frame, kpi)
                    
                    algorithms_performance.append(alg_avg)
                    
                    if kpi == 'ete_latency':
                        net_avg = DataFrame.calculate_average(alg_data_frame, 'net_latency')
                        algorithms_performance.append(net_avg)
                    elif kpi == 'energy':
                        hmd_energy_avg = DataFrame.calculate_average(alg_data_frame, 'hmd_energy')
                        algorithms_performance.append(hmd_energy_avg)
                    
                    alg_std = DataFrame.calculate_std(alg_data_frame, kpi)
                    
                    if kpi == 'successful' or kpi == 'unsuccessful' or kpi == 'exec':
                        alg_std = alg_std / 10
                    
                    algorithms_performance.append(alg_std)
                
                CSV.save_data(city_dir, file_name,algorithms_performance )
                x_value += 450
                
    @staticmethod
    def create_bar_plots(overleaf_dir: str, results: dict):
        global bar_plot_kpis
        for kpi in bar_plot_kpis:
            BarPlot.create_bar_plot(overleaf_dir, results, kpi)
            
    
class LinePlot:
    
    """
    all methods receive a DataFrame and produces a csv file that will be used by overleaf
    """
    @staticmethod
    def create_x_row():
        x_row = []
        for i in range(1, 301):
            x_row.append(round((i / 30), 2))
        
        #print(x_row)
        return x_row
    
    @staticmethod 
    def create_line_plot(overleaf_dir: str, results: dict, kpi: str):
        """
        1. first row is x and this represents the time in hours (10h). 
        2. X row is generated based on a loop that ranges from 1 to 300, each value of each line of X is calculated based on: iteration/300. 
        3. reads each file, delete the first result, and get first 100 values of it in each radius. in the end, there will be 300 values for the 3 radius. Store them on a list.
        """
        for city, radius in results.items():
            city_dir = '{}{}/'.format(overleaf_dir, city)
            file_name = '{}_{}_line.csv'.format(city, kpi)
            file_headers = Results.get_line_plot_file_header()
                
             
            CSV.create_file(city_dir, file_name, file_headers)
            
            x_row = LinePlot.create_x_row()
            position = 0
            
            for radius_id, algorithms in radius.items():
                #print(f'radius: {radius_id}')
                for i in range(100):
                    line_list = []
                    line_list.append(x_row[position])
                    for algorithm, alg_data_frame in algorithms.items():
                        kpi_result = alg_data_frame[kpi].iloc[i]
                        line_list.append(kpi_result)
                
                    #print(line_list)
                    CSV.save_data(city_dir, file_name, line_list)
                    position += 1   
                
            
class BoxPlot:
    @staticmethod 
    def create_boxplot(overleaf_dir: str, results: dict, kpi: str):
        """for each radius, it creates files without X column for overleaf boxplot"""
        for city, radius in results.items():
            city_dir = '{}{}/'.format(overleaf_dir, city)
            
            for radius_id, algorithms in radius.items():
                
                file_name = '{}_{}_{}_box.csv'.format(city, kpi, radius_id)
                file_headers = Results.get_box_plot_file_header()
                
                CSV.create_file(city_dir, file_name, file_headers)
            
                min_lines = float('inf')
                for algorithm, alg_data_frame in algorithms.items():
                    number_lines = len(alg_data_frame)
                    if number_lines < min_lines:
                        min_lines = number_lines
                        
                for i in range(min_lines):
                    line_list = []
                    for algorithm, alg_data_frame in algorithms.items():
                        kpi_result = alg_data_frame[kpi].iloc[i]
                        line_list.append(kpi_result)
                
                    CSV.save_data(city_dir, file_name, line_list)

    @staticmethod
    def print_message(algorithm, median_value, means, q1, q3, lower_whisker, upper_whisker, lower_outliers, upper_outliers):
        a = textwrap.dedent("""\
        legend
        \\addplot+[
            boxplot prepared={
                median=median_value,
                average=means,
                lower quartile=lower_quartile,
                upper quartile=upper_quartile,
                lower whisker=lower_whisker,
                upper whisker=upper_whisker
            },
        ]
        table 
        """)
        
        a = a.replace("median_value", median_value)
        a = a.replace("means", means)
        a = a.replace("lower_quartile", q1)
        a = a.replace("upper_quartile", q3)
        a = a.replace("lower_whisker", lower_whisker)
        a = a.replace("upper_whisker", upper_whisker)
        
        if algorithm:
            a = a.replace("legend", "\\addlegendentry{algorithm}")
            a = a.replace("algorithm", algorithm)
        else:
            a = a.replace("legend", "")
            
        
        if not lower_outliers and not upper_outliers:
            a = a.replace("table", "coordinates {};")
            
        else:
            outliers = ''
            for outlier in lower_outliers:
                outliers = f"{outliers}{str(outlier)}{chr(92)}{chr(92)} "
            for outlier in upper_outliers:
                outliers = f"{outliers}{str(outlier)}{chr(92)}{chr(92)} "
            
            a = a.replace("table", "table[row sep=row_sep,y index=0] {outliers};")
            a = a.replace("row_sep", f"{chr(92)}{chr(92)}")
            a = a.replace("outliers", outliers)
        
        
        print(a)

    @staticmethod
    def get_boxplot_data_from_plt(data_list):
        data = [data_list]
        bp = plt.boxplot(data, showmeans=True)
        medians = [round(item.get_ydata()[0], 1) for item in bp['medians']]
        means = [round(item.get_ydata()[0], 1) for item in bp['means']]
        minimums = [round(item.get_ydata()[0], 1) for item in bp['caps']][::2]
        maximums = [round(item.get_ydata()[0], 1) for item in bp['caps']][1::2]
        q1 = [round(min(item.get_ydata()), 1) for item in bp['boxes']]
        q3 = [round(max(item.get_ydata()), 1) for item in bp['boxes']]
        fliers = [item.get_ydata() for item in bp['fliers']]
        lower_outliers = []
        upper_outliers = []
        for i in range(len(fliers)):
            lower_outliers_by_box = []
            upper_outliers_by_box = []
            for outlier in fliers[i]:
                if outlier < q1[i]:
                    lower_outliers_by_box.append(round(outlier, 1))
                else:
                    upper_outliers_by_box.append(round(outlier, 1))
            lower_outliers.append(lower_outliers_by_box)
            upper_outliers.append(upper_outliers_by_box)    
            
        
        stats = [medians, means, minimums, maximums, q1, q3, lower_outliers, upper_outliers]
        stats_names = ['median', 'means', 'lower_whisker', 'upper_whisker', 'q1', 'q3', 'lower_outliers', 'upper_outliers']
        categories = ['DATASET 1'] # to be updated
        result = {
            "median": None,
            "means": None,
            "q1": None,
            "q3": None,
            "lower_whisker": None,
            "upper_whisker": None,
            "lower_outliers": [],
            "upper_outliers": [],
            
        }
        for i in range(len(categories)):
            #print(f'\033[1m{categories[i]}\033[0m')
            for j in range(len(stats)):
                #print(f'{stats_names[j]}: {stats[j][i]}')
                result[stats_names[j]] = stats[j][i]
            #print('\n')
        return result

    @staticmethod
    def calculate_boxplot_data(overleaf_dir: str, cities: dict, algorithms: list, resolutions: list):
        
        for resolution in resolutions:    
            print(f'\n%############### RESOLUTION {resolution} ###############\n')
            for city, radius in cities.items():
                plot = True
                city_dir = '{}{}/'.format(overleaf_dir, city)
                print(f'\n%############### {city.upper()} ###############\n')
                for r in radius: 
                    radius_name = 'r_0{}'.format(r)
                    print(f'\n%############### RADIUS {radius_name} ###############\n')
                    file_name = '{}_{}_{}_box'.format(city, resolution, radius_name)
                    #print(file_name)
                    file_data = DataFrame.get_df_data(city_dir, file_name)
                    
                    for algorithm in algorithms:
                        
                        algo_list = file_data[algorithm].values.tolist()
                        boxplot_data = BoxPlot.get_boxplot_data_from_plt(algo_list)
                        #pprint(boxplot_data)
                        algorithm_id = None
                        if plot:
                            algorithm_id = algorithm[:2].upper()
                        
                        BoxPlot.print_message(
                            algorithm_id, 
                            str(boxplot_data['median']),
                            str(boxplot_data['means']),
                            str(boxplot_data['q1']),
                            str(boxplot_data['q3']),
                            str(boxplot_data['lower_whisker']),
                            str(boxplot_data['upper_whisker']),
                            boxplot_data['lower_outliers'],
                            boxplot_data['upper_outliers']
                        )
                    plot = False
                    
                    
                a = input('')
            
            print(f'\n%############### FINISHED ###############\n')
                        
        """ 
        a = input('continue baby')
        
        
        for city in cities:
            city_dir = '{}{}/'.format(overleaf_dir, city)
            for file_name in os.listdir(city_dir):
                print(file_name)
                f_name = file_name.replace('.csv', '')
                file_data = DataFrame.get_df_data(city_dir, f_name)
                #print(file_data)
                for algorithm in algorithms:
                    
                    algo_list = file_data[algorithm].values.tolist()
                    boxplot_data = BoxPlot.get_boxplot_data_from_plt(algo_list)
                    #pprint(boxplot_data)
                    BoxPlot.print_message(
                        algorithm[:2].upper(), 
                        str(boxplot_data['median']),
                        str(boxplot_data['means']),
                        str(boxplot_data['q1']),
                        str(boxplot_data['q3']),
                        str(boxplot_data['lower_whisker']),
                        str(boxplot_data['upper_whisker']),
                        boxplot_data['lower_outliers'],
                        boxplot_data['upper_outliers']
                    )
                #print(f'{file_name:_<20}')
                print(f'\n##############################\n')
                a = input('')
                    #a = input('')
                #a = input('')
            #a = input('')
        """
        
        
        


                
class CDF:
    
    @staticmethod
    def generate_index(cdf_list):
        return cdf_list.ps
    
    def generate_probabilites(cdf_list):
        return cdf_list.qs
        
    
    @staticmethod
    def print_CDF(CDF):
        #print(CDF)
        index = 0
        for c in CDF:
            print(CDF.ps[index])
            index+=1
        print('\n')
        
        index = 0
        for c in CDF:
            print(CDF.qs[index])
            index+=1
        print('\n')
        
        #a = input('')
        
    @staticmethod
    def print_CDF2(CDF):
        print(CDF)
        print('__________________________________')
        threshold = 0.1
        for i in range(0, 16):
            if CDF.ps[i] > threshold:
                #print(f'{round(CDF.ps[i], 1)} -> {CDF.qs[i]}')
                print(f'{CDF.ps[i]}')
                
                threshold += 0.1
                if threshold >= 1:
                    break
    
    @staticmethod
    def generate_cdf(overleaf_dir: str, results: dict, kpi: str):
        
        kpi_data = results[[kpi]]
        print(kpi_data)
        a = input('')
        cdf_data = Cdf.from_seq(kpi_data)
        CDF.print_CDF(cdf_data)
                
            
if __name__ == "__main__":
    
    cities = {
        'bern':   [18, 23, 29],
        'geneva': [15, 17, 19],
        'zurich': [16, 19, 22]       
    }
    
    resolutions = ['8k', '4k', '1440p', '1080p']
    
    overleaf_dir = '/home/ubuntu/overleaf/'
    algorithms = ['dscp', 'scg', 'lra', 'la', 'am']
    BoxPlot.calculate_boxplot_data(overleaf_dir, cities, algorithms, resolutions)

    '''
    overleaf_dir = '/home/ubuntu/overleaf/'
    
    
    bar_plot_kpis = ['ete_latency', 'energy', 'successful', 'unsuccessful', 'exec']
    
    Results.create_overleaf_topology_directories_(overleaf_dir, cities)
    results = Results.read_files(RESULTS_DIR, cities, algorithms)
    #BarPlot.create_bar_plots(overleaf_dir, results)
    #LinePlot.create_line_plot(overleaf_dir, results, 'ete_latency')
    BoxPlot.create_boxplot(overleaf_dir, results, '1080p')
    BoxPlot.create_boxplot(overleaf_dir, results, '1440p')
    BoxPlot.create_boxplot(overleaf_dir, results, '4k')
    BoxPlot.create_boxplot(overleaf_dir, results, '8k')
    '''
    
    """
    df = DataFrame.get_df_data('/home/ubuntu/scg/utils/', 'early')
    
    cdf_data = {
        "120": [],
        "90": [],
        "72": []
    }
    for index, row in df.iterrows():
        cdf_data['120'].append(row["y1"])
        cdf_data['90'].append(row["y2"])
        cdf_data['72'].append(row["y3"])
        #cdf_data.append(row["y1"])
        
    
    def ecdf(a):
        x, counts = np.unique(a, return_counts=True)
        cusum = np.cumsum(counts)
        return x, cusum / cusum[-1]
    
    def plot_ecdf(a,b,c):
        x, y = ecdf(a)
        x = np.insert(x, 0, x[0])
        y = np.insert(y, 0, 0.)
        plt.plot(x, y, drawstyle='steps-post')
        
        
        x, y = ecdf(b)
        x = np.insert(x, 0, x[0])
        y = np.insert(y, 0, 0.)
        plt.plot(x, y, drawstyle='steps-post')
        
        x, y = ecdf(c)
        x = np.insert(x, 0, x[0])
        y = np.insert(y, 0, 0.)
        plt.plot(x, y, drawstyle='steps-post')
        
        plt.grid(True)
        plt.show()
    
    a = cdf_data['120']
    b = cdf_data['90']
    c = cdf_data['72']
    plot_ecdf(a, b, c)

    
    a = input('STOP!')
    
    
    #pprint(cdf_data)
        
    #a = input('TYPE TO CONTINUE!')
    #new_cdf_data = Cdf.from_seq(cdf_data)
    new_cdf_data = {
        "120": Cdf.from_seq(cdf_data['120']),
        "90": Cdf.from_seq(cdf_data['90']),
        "72": Cdf.from_seq(cdf_data['72'])
    }
        
    
    #cdf_probabilities = CDF.generate_probabilites(new_cdf_data)
    #cdf_index  = CDF.generate_index(new_cdf_data)
    
    results = {
        "120": {
            "index": CDF.generate_index(new_cdf_data['120']),
            "probabilities": CDF.generate_probabilites(new_cdf_data['120'])
        },
        "90": {
            "index": CDF.generate_index(new_cdf_data['90']),
            "probabilities": CDF.generate_probabilites(new_cdf_data['90'])
        },
        "72": {
            "index": CDF.generate_index(new_cdf_data['72']),
            "probabilities": CDF.generate_probabilites(new_cdf_data['72'])
        }
    }
    
    
    '''total = 26
    threshold = 0.625
    aux = None
    new_list = []
    for i in results['72']['probabilities']:    
        
        if threshold > 0.625:
            #value = (i + aux) / 2
            new_list.append(0)   
            threshold = 0
        
        new_list.append(i)
        
        threshold += 0.625
        aux = i'''
    
    
    
    len_120 = len(results['120']['probabilities'])
    len_90 = len(results['90']['probabilities'])
    len_72 = len(results['72']['probabilities'])
    
    file_headers = ['x', '120', 'y', '90', 'z', '72']
    CSV.create_file('/home/ubuntu/scg/utils/', 'fps_cdf.csv', file_headers)
    i = 0
    for value in results['120']['index']:
        data = []
        if i > len_120-1:
            data.append('')
            data.append('')
        else:
            data.append(results['120']['probabilities'][i])
            data.append(results['120']['index'][i])
        
        if i > len_90-1:
            data.append('')
            data.append('')
        else:
            data.append(results['90']['probabilities'][i])
            data.append(results['90']['index'][i])
        
        if i > len_72-1:
            data.append('')
            data.append('')
        else:
            data.append(results['72']['probabilities'][i])
            data.append(results['72']['index'][i])
        
        
        #data.append(cdf_probabilities[i])
        #data.append(cdf_index[i])
        CSV.save_data('/home/ubuntu/scg/utils/', 'fps_cdf.csv', data)
        i += 1

        
    """
