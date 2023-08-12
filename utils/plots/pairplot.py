import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.ticker import ScalarFormatter, FuncFormatter

# Read the CSV file
df = pd.read_csv('merged.csv')

hue_order = ['flatwise', 'wsp']

# Filter specific lines based on values in a column
#filtered_data = df[df['scenario'] == 'scenario 1']

# Select specific columns
selected_columns = ['topology_radius', 'algorithm', 'flow_e2e_latency', 'flow_latency', 'route_latency', 'overp_net_latency']
#selected_columns = ['scenario', 'algorithm', 'standard_8k', 'standard_4k', 'standard_2k', 'standard_1k']
#selected_columns = ['scenario', 'algorithm', 'high_8k', 'high_4k', 'high_2k', 'high_1k']
filtered_data = df[selected_columns]

# subplot_height = 2.0
# height=subplot_height

# Generate the pairplot with hue as 'algorithm' if available
pair_grid = sns.pairplot(filtered_data, hue="algorithm", hue_order=hue_order, plot_kws={'s': 5})
pair_grid._legend.remove()    

formatter = FuncFormatter(lambda x, pos: "{:.1f}".format(x))

# Enable scientific notation for tick labels on y-axis
for ax in pair_grid.axes.flat:
    if ax.get_ylabel():
        ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax.ticklabel_format(axis='both', style='sci', scilimits=(0, 0))
        ax.yaxis.set_label_coords(-0.15, 0.5)
    
    # elif ax.get_xlabel():
        # print(ax.get_xlabel())
        # custom_notation = '1e5'
        # x_position = 0.95  # Adjust the x-coordinate for the custom notation position
        # y_position = 0.07  # Adjust the y-coordinate for the custom notation position

        # ax.xaxis.get_offset_text().set_visible(False)  # Hide default notation
        # ax.text(x_position, y_position, custom_notation, transform=ax.transAxes, va='top', ha='right', fontsize=10) 
        

"""    
pair_grid.axes[0,0].yaxis.set_label_text('Network congestion (%)', visible=True)
pair_grid.axes[3,0].xaxis.set_label_text('Network congestion (%)', visible=True)

custom_notation = 'x10\u00b9'
x_position = -2.2  # Adjust the x-coordinate for the custom notation position
y_position = 0.12  # Adjust the y-coordinate for the custom notation position
pair_grid.axes[3,0].xaxis.get_offset_text().set_visible(False)  # Hide default notation
pair_grid.axes[3,0].text(x_position, y_position, custom_notation, transform=ax.transAxes, va='top', ha='right', fontsize=10)

x_position = -3  # Adjust the x-coordinate for the custom notation position
y_position = 4.1  # Adjust the y-coordinate for the custom notation position
pair_grid.axes[0,0].yaxis.get_offset_text().set_visible(False)  # Hide default notation
pair_grid.axes[0,0].text(x_position, y_position, custom_notation, transform=ax.transAxes, va='top', ha='right', fontsize=10)

###############

pair_grid.axes[1,0].yaxis.set_label_text('Network throughput (Mbps)', visible=True)
pair_grid.axes[3,1].xaxis.set_label_text('Network throughput (Mbps)', visible=True)

custom_notation = 'x10\u2075'
x_position = -1.15  # Adjust the x-coordinate for the custom notation position
y_position = 0.12  # Adjust the y-coordinate for the custom notation position
pair_grid.axes[3,1].xaxis.get_offset_text().set_visible(False)  # Hide default notation
pair_grid.axes[3,1].text(x_position, y_position, custom_notation, transform=ax.transAxes, va='top', ha='right', fontsize=10)


x_position = -3  # Adjust the x-coordinate for the custom notation position
y_position = 3.1  # Adjust the y-coordinate for the custom notation position
pair_grid.axes[1,0].yaxis.get_offset_text().set_visible(False)  # Hide default notation
pair_grid.axes[1,0].text(x_position, y_position, custom_notation, transform=ax.transAxes, va='top', ha='right', fontsize=10)

########################################################################################################################

pair_grid.axes[2,0].yaxis.set_label_text('Network latency (ms)', visible=True)
pair_grid.axes[3,2].xaxis.set_label_text('Network latency (ms)', visible=True)

########################################################################################################################

pair_grid.axes[3,0].yaxis.set_label_text('Video resolution FPS', visible=True)
pair_grid.axes[3,3].xaxis.set_label_text('Video resolution FPS', visible=True)
custom_notation = 'x10\u00b9'
x_position = 0.2  # Adjust the x-coordinate for the custom notation position
y_position = 0.12  # Adjust the y-coordinate for the custom notation position
pair_grid.axes[3,3].xaxis.get_offset_text().set_visible(False)  # Hide default notation
pair_grid.axes[3,3].text(x_position, y_position, custom_notation, transform=ax.transAxes, va='top', ha='right', fontsize=10)

x_position = -3  # Adjust the x-coordinate for the custom notation position
y_position = 1  # Adjust the y-coordinate for the custom notation position
pair_grid.axes[3,0].yaxis.get_offset_text().set_visible(False)  # Hide default notation
pair_grid.axes[3,0].text(x_position, y_position, custom_notation, transform=ax.transAxes, va='top', ha='right', fontsize=10)

    
new_labels = ["WPAR", "WLARP", "EEWRP"]

colors = sns.color_palette()

handles = [
    plt.Line2D([], [], color=colors[0], label=new_labels[0]),
    plt.Line2D([], [], color=colors[1], label=new_labels[1]),
    plt.Line2D([], [], color=colors[2], label=new_labels[2])
]

#plt.legend(handles=handles)
plt.legend(handles=handles, loc='lower center', bbox_to_anchor=(-1.11, -0.48), ncol=3, title='')
plt.subplots_adjust(bottom=0.22)
plt.savefig("/Users/alisson-cds/Downloads/plots/pairplot.pdf", format="pdf", bbox_inches='tight')
"""
plt.show()