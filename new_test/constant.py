import numpy as np
from solcore.light_source import LightSource
# import matplotlib.pyplot as plt
T=300
vint = np.linspace(-6, 4, 1000)
V = np.linspace(-3, 0, 1000)  # np
wl = np.linspace(350, 2000, 1000) *1e-9   # version1
light_source = LightSource(source_type="standard"
                           , version="AM1.5g"
                           , x=wl
                           , output_units="photon_flux_per_m"
                           , concentration=1
                           )
if __name__ == '__main__':
    print('T', T)
    print('vint', vint)
    print('V', V)
    print('wl', wl)
    # plt.plot(wl)
    # plt.show()