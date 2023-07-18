import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

#sns.set_theme(style="darkgrid")

data = pd.read_csv(r'C:\\Users\\Alisson Cds\Downloads\\vr_streaming\\utils\\merged_file.csv')

# Subset the columns of interest
subset_data = data[['scenario', 'algorithm', 'net_latency']]

# Melt the data for bar plot
melted_data = pd.melt(subset_data, id_vars=['scenario', 'algorithm'], value_vars=['net_latency'], var_name='Bandwidth Type', value_name='FPS')

# Set up the bar plots for each scenario
g = sns.FacetGrid(melted_data, col='scenario', col_wrap=3, height=4)
g.map_dataframe(sns.barplot, x='Bandwidth Type', y='FPS', hue='algorithm', ci='sd', capsize=0.1, palette='Set3')
g.set_titles('Scenario {col_name}')
g.set_xlabels('Bandwidth Type')
g.set_ylabels('FPS')
g.add_legend(title='Algorithm')
plt.tight_layout()
plt.show()

'''

# ECDF plots
# Subset the columns of interest
subset_data = data[['scenario', 'algorithm', 'total_allocate_bw', 'expected_allocated_bw', 'updated_allocated_bw']]

# Melt the data for facetting
melted_data = pd.melt(subset_data, id_vars=['scenario', 'algorithm'], value_vars=['total_allocate_bw', 'expected_allocated_bw', 'updated_allocated_bw'], var_name='Bandwidth Type', value_name='Bandwidth')

# Set up the facetted ECDF plot
g = sns.FacetGrid(melted_data, col='Bandwidth Type', hue='algorithm', col_wrap=3, height=4)
g.map(sns.ecdfplot, 'Bandwidth').add_legend(title='Algorithm')
g.fig.subplots_adjust(top=0.9)
g.fig.suptitle('ECDF of Bandwidth Allocation')
plt.show()



#BOXENPLOT
# Subset the columns of interest
subset_data = data[['scenario', 'algorithm', 'total_allocate_bw', 'expected_allocated_bw', 'updated_allocated_bw']]

# Melt the data for boxenplot
melted_data = pd.melt(subset_data, id_vars=['scenario', 'algorithm'], value_vars=['total_allocate_bw', 'expected_allocated_bw', 'updated_allocated_bw'], var_name='Bandwidth Type', value_name='Bandwidth')

# Set up the boxenplot
plt.figure(figsize=(12, 8))
sns.boxenplot(x='Bandwidth Type', y='Bandwidth', hue='algorithm', data=melted_data, palette='Set3')
plt.title('Bandwidth Allocation')
plt.xlabel('Bandwidth Type')
plt.ylabel('Bandwidth')
plt.legend(title='Algorithm')
plt.show()





a = input('')
# HEATMAP FOR NETOWRK CONGESTION LEVELS

# Aggregate congestion levels by taking the average
agg_data = data.groupby(['scenario', 'algorithm'])['net_congested_level'].mean().reset_index()

# Create a pivot table to reshape the data for heatmap
heatmap_data = agg_data.pivot(index='scenario', columns='algorithm', values='net_congested_level')

# Set up the heatmap plot
plt.figure(figsize=(12, 8))
sns.heatmap(heatmap_data, annot=True, cmap='YlGnBu', cbar=True, linewidths=0.5)
plt.title('Network Congestion Levels')
plt.xlabel('Algorithm')
plt.ylabel('Scenario')
plt.show()
'''