import numpy as np
import os
import shutil
kb =  1.38e-23
T = 298
dn = np.array([1e14, 1e15, 1e16])
diff = kb*T*np.log((3e3+dn)*(3e16+dn)/1e20)
print(diff/1.6e-19)
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import numpy as np
import mpld3
num_colors = 25

# Get the tab10 colorma

# Create a normalizer to map values to colors
norm = Normalize(vmin=0, vmax=num_colors - 1)

colors = [plt.cm.hsv(i/num_colors) for i in range(num_colors)]
# Get the colors from the colormap
colors = [cmap(norm(i)) for i in range(num_colors)]

# Display the colors
for i, color in enumerate(colors):
    plt.plot([i, i+1], [0, 1], color=color, label=f'Color {i+1}')

plt.legend()
plt.show()
# Generate some data
# x = np.linspace(0, 10, 100)
# y = np.sin(x)
#
# # Create a plot
# fig, ax = plt.subplots()
# ax.plot(x, y)
#
# # Make the plot interactive
# # interactive_plot = mpld3.display(fig)
#
# # Save the interactive plot as an HTML file
# mpld3.save_html(fig, "interactive_plot.html")
#
# def movefile(file, direction):
#     current_path = os.getcwd()
#     save_path = os.path.join(current_path, direction)
#     fig1_loc = os.path.join(current_path, file)
#     fig1_loc_new = os.path.join(save_path, file)
#     shutil.move(fig1_loc, fig1_loc_new)
# movefile("interactive_plot.html", "referance_all_solar_cell" )
# plt.show()