#how lace the legend slightly below the its current position in the following code?

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv(r'/Users/alisson-cds/Downloads/merged_file.csv')

fig, axes = plt.subplots(1, 4, figsize=(15, 4))

# Define the order of scenarios and algorithms
scenario_order = ['scenario 1', 'scenario 2', 'scenario 3', 'scenario 4']
algorithm_order = ['alg1', 'alg2', 'alg3']

# Create the FacetGrid plot
g = sns.FacetGrid(df, col='scenario', col_order=scenario_order, hue='algorithm', hue_order=algorithm_order)

# Plot the ECDF for 'total_allocate_bw' and adjust scientific notation position
def plot_ecdf(x, **kwargs):
    sns.ecdfplot(x, **kwargs)
    ax = plt.gca()
    ax.ticklabel_format(axis='x', style='sci', scilimits=(0, 0), useLocale=True)
    ax.xaxis.get_offset_text().set_visible(False)  # Hide default notation

    # Add custom notation
    custom_notation = '1e5'
    x_position = 0.87  # Adjust the x-coordinate for the custom notation position
    y_position = 0.07  # Adjust the y-coordinate for the custom notation position
    ax.text(x_position, y_position, custom_notation, transform=ax.transAxes, va='top', ha='right', fontsize=10)
    
g.map(plot_ecdf, 'total_allocate_bw')

# Set plot labels and titles
g.set_axis_labels('Network Bandwidth Allocation (Mbps)', 'ECDF')
# Customize subplot titles
g.set_titles('Scenario: {col_name}')


# Add a legend with custom labels and colors
legend_labels = ['Algorithm1', 'Algorithm2', 'Algorithm3']
legend_colors = sns.color_palette(n_colors=len(legend_labels))
legend_handles = [plt.Line2D([0], [0], color=color, lw=2) for color in legend_colors]
g.add_legend(handles=legend_handles, labels=legend_labels, title='', loc='lower center', bbox_to_anchor=(0.5, -0.08), ncol=3, frameon=True)

plt.suptitle('')
#plt.subplots_adjust(upper=-0.1)  # Adjust the top margin to make space for the suptitle
plt.subplots_adjust(bottom=0.4)  # Adjust the bottom margin to make space for the legend
plt.subplots_adjust(wspace=0.3)
plt.tight_layout()
plt.show()