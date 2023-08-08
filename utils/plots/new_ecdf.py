#why the colors blue, orange, and green defined in handles are not of the same intensity as the original colors in the displot legend?

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv(r'/Users/alisson-cds/Downloads/merged_file.csv')

scenario_order = ['scenario 1', 'scenario 2', 'scenario 3', 'scenario 4']
hue_order = ['alg1', 'alg2', 'alg3']

d = sns.displot(df, 
                x="average_fps", 
                kind="ecdf", 
                col='scenario', 
                hue='algorithm', 
                hue_order=hue_order,  
                height=3.5, 
                aspect=.9, 
                legend=False
)
fig = d.fig
#fig.suptitle("Custom Super Title")
a0 = fig.axes[0]
a1 = fig.axes[1]
a2 = fig.axes[2]
a3 = fig.axes[3]

a0.set_title("Scenario 1", fontdict={'size': 10})
a1.set_title("Scenario 2", fontdict={'size': 10})
a2.set_title("Scenario 3", fontdict={'size': 10})
a3.set_title("Scenario 4", fontdict={'size': 10})

a0.set_xlabel("FPS", fontdict={'size': 10})
a1.set_xlabel("FPS", fontdict={'size': 10})
a2.set_xlabel("FPS", fontdict={'size': 10})
a3.set_xlabel("FPS", fontdict={'size': 10})   

# Add custom notation
custom_notation = 'x10\u00b9'
x_position = 1  # Adjust the x-coordinate for the custom notation position
y_position = 0.07  # Adjust the y-coordinate for the custom notation position

a0.xaxis.get_offset_text().set_visible(False)  # Hide default notation
a0.text(x_position, y_position, custom_notation, transform=a0.transAxes, va='top', ha='right', fontsize=10) 

a1.xaxis.get_offset_text().set_visible(False)  # Hide default notation
a1.text(x_position, y_position, custom_notation, transform=a1.transAxes, va='top', ha='right', fontsize=10) 

a2.xaxis.get_offset_text().set_visible(False)  # Hide default notation
a2.text(x_position, y_position, custom_notation, transform=a2.transAxes, va='top', ha='right', fontsize=10) 

a3.xaxis.get_offset_text().set_visible(False)  # Hide default notation
a3.text(x_position, y_position, custom_notation, transform=a3.transAxes, va='top', ha='right', fontsize=10) 

plt.ticklabel_format(axis='x', style='scientific', scilimits=(0,0))
plt.ticklabel_format(axis='y', style='plain', scilimits=(0,0))

new_labels = ["Algorithm 1", "Algorithm 2", "Algorithm 3"]

colors = sns.color_palette()

handles = [
    plt.Line2D([], [], color=colors[0], label=new_labels[0]),
    plt.Line2D([], [], color=colors[1], label=new_labels[1]),
    plt.Line2D([], [], color=colors[2], label=new_labels[2])
]

#plt.legend(handles=handles)
plt.legend(handles=handles, loc='lower center', bbox_to_anchor=(-1.11, -0.33), ncol=3, title='')
plt.subplots_adjust(bottom=0.22)
#plt.savefig("/Users/alisson-cds/Downloads/plots/ecdf.pdf", format="pdf", bbox_inches='tight')
plt.show()
