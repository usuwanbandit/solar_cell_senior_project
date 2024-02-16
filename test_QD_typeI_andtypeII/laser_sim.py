import numpy as np
import matplotlib.pyplot as plt
from solcore.light_source import LightSource

wl = np.linspace(300, 3000, 200)

color_laser = np.linspace(300, 1400, 11)
color_collection = []
for i in color_laser:
    color_collection.append(LightSource(source_type='laser', x=wl, center=i, linewidth=50))
plt.figure(1)
for count, i in enumerate(color_collection):
    plt.plot(i.spectrum(), label=f"{color_laser[count]}")
plt.show()
