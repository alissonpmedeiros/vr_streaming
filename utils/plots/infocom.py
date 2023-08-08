# Consider the following python seaborn lmplot and show me how to change the font size of each subplot ylabel and xlabel as well as the x and y ticks to font size 12 and font times new roman.

import matplotlib
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import ScalarFormatter, FuncFormatter

# Set the font family and size
font = {'family': 'serif', 'size': 13}
matplotlib.rc('font', **font)

def generate_lmplot(column_name, ylabel_name, legend_flag, subtitle_flag, xticks_flag):
    hue_order = ["alg1", "alg2", "alg3"]
    df = pd.read_csv(r'/Users/alisson-cds/Downloads/merged_file.csv')

    g = sns.lmplot(
        data=df, 
        x="average_fps", 
        y=column_name, 
        hue="algorithm",
        hue_order=hue_order,
        col="scenario", 
        #row="scenario", 
        height=3.5, 
        aspect=.9, 
        scatter_kws={"s": 5, "alpha": 0.6, "edgecolor": "none"}, 
        legend=False,
        # markers=["o", "D", "*"],
    )

    g.set(ylabel=ylabel_name)

    fig = g.fig
    #fig.suptitle("Custom Super Title")
    a0 = fig.axes[0]
    a1 = fig.axes[1]
    a2 = fig.axes[2]
    a3 = fig.axes[3]
    
    if subtitle_flag:
        a0.set_title("Scenario 1", fontdict={'size': 13})
        a1.set_title("Scenario 2", fontdict={'size': 13})
        a2.set_title("Scenario 3", fontdict={'size': 13})
        a3.set_title("Scenario 4", fontdict={'size': 13})
    else:
        a0.set_title("", fontdict={'size': 13})
        a1.set_title("", fontdict={'size': 13})
        a2.set_title("", fontdict={'size': 13})
        a3.set_title("", fontdict={'size': 13})
    
    if xticks_flag:
        a0.set_xlabel("Average FPS", fontdict={'size': 13})
        a1.set_xlabel("Average FPS", fontdict={'size': 13})
        a2.set_xlabel("Average FPS", fontdict={'size': 13})
        a3.set_xlabel("Average FPS", fontdict={'size': 13})
    else: 
        a0.set_xlabel("", fontdict={'size': 13})
        a1.set_xlabel("", fontdict={'size': 13})
        a2.set_xlabel("", fontdict={'size': 13})
        a3.set_xlabel("", fontdict={'size': 13})
    
    axes = g.axes.flatten()
    first_subplot_axes = axes[0]
    second_subplot_axes = axes[1]
    third_subplot_axes = axes[2]
    fourfh_subplot_axes = axes[3]
    
    if not xticks_flag:
        for ax in g.axes.flatten():
            # Hide x and y axis tick labels
            ax.set_xticklabels([])

    # Draw a horizontal line in the first subplot
    first_subplot_axes.axhline(y=1000, color='r', linestyle='dotted', linewidth=0.7, )
    second_subplot_axes.axhline(y=2000, color='r', linestyle='dotted', linewidth=0.7)
    third_subplot_axes.axhline(y=3000, color='r', linestyle='dotted', linewidth=0.7)
    fourfh_subplot_axes.axhline(y=4000, color='r', linestyle='dotted', linewidth=0.7)
    
    first_subplot_axes.yaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))

    plt.ylim(0, 4000, 1000)
    plt.yticks([1000, 2000, 3000, 4000])


    plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
    
    
    
    
    if legend_flag:
        plt.legend(loc='lower center', bbox_to_anchor=(-1.11, -0.47), ncol=3)
        legend = plt.gca().get_legend()
        handles, labels = legend.legendHandles, legend.get_texts()

        # Increase the marker size
        for handle in handles:
            handle.set_sizes([30])
            
        new_labels = ["WPAR", "WLARP", "EEWRP"]

        # Assign custom labels to the legend
        for text, label in zip(labels, new_labels):
            text.set_text(label)

    plt.subplots_adjust(bottom=0.28)
    plt.subplots_adjust(wspace=0.03)
    
    plt.savefig("/Users/alisson-cds/Downloads/plots/{}.pdf".format(column_name), format="pdf", bbox_inches='tight')
    # plt.show()



generate_lmplot("standard_8k", 'Standard 8K video res.', False, True, False)
generate_lmplot("high_8k", 'High 8K video res.', False, False, False)
generate_lmplot("full_8k", 'High 8K video res. (60 FPS)', True, False, True)


'''
# Create a figure with subplots
#fig, axes = plt.subplots(nrows=2, ncols=4, figsize=(16, 8))

# Flatten the axes array for easier iteration
#axes = axes.flatten()

# Generate the lmplot for each scenario and column
for i, column in enumerate(columns):
    # Filter the DataFrame for the current scenario and column
    data = df[(df['scenario'] == scenarios[0]) & (df['algorithm'].isin(algorithms))]

    # Plot the lmplot on the corresponding subplot
    #sns.lmplot(x='average_fps', y=column, hue='algorithm', data=data, scatter=True, ci=None)

    # Set the title
    #axes[i].set_title(f'Scenario {scenarios[0]} - {column}')
    
    sns.lmplot(
        data=data, x="average_fps", y=column,
        height=3, hue='algorithm',
        facet_kws=dict(sharex=False, sharey=False),
    )

# Adjust the spacing between subplots
#plt.tight_layout()

# Show the plot
plt.show()
'''


'''
# Generate the lmplot for each scenario and column
for scenario in scenarios:
    for column in columns:
        # Filter the DataFrame for the current scenario and column
        data = df[(df['scenario'] == scenario) & (df['algorithm'].isin(algorithms))]
        
        # Plot the lmplot
        sns.lmplot(x='average_fps', y=column, hue='algorithm', data=data, scatter=True, ci=None)
        
        # Set the title
        plt.title(f'Scenario {scenario} - {column}')
        
        # Show the plot
        plt.show()
'''






'''
# Subset the columns of interest
subset_data = data[['scenario', 'algorithm', 'net_latency']]

# Melt the data for bar plot
melted_data = pd.melt(subset_data, id_vars=['scenario', 'algorithm'], value_vars=['net_latency'], var_name='Bandwidth Type', value_name='FPS')



# Set up the bar plots for each scenario
g = sns.FacetGrid(melted_data, col='scenario', col_wrap=4, height=4)
#g.map_dataframe(sns.barplot, x='Bandwidth Type', y='FPS', hue='algorithm', ci='sd', capsize=0.1, palette='Set3')
g.map_dataframe(sns.lmplot, x="average_fps", y="full_8k", hue="algorithm")
g.set_titles('Scenario {col_name}')
g.set_xlabels('Average FPS')
g.set_ylabels('8K resolution')
g.add_legend(title='Algorithm')
plt.tight_layout()
plt.show()
'''

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