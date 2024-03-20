import numpy as np
from solcore import constants
from solcore.light_source import LightSource
# import matplotlib.pyplot as plt
T=300
vint = np.linspace(-3, 3, 1000)
wl = np.linspace(350, 1200, 1000) *1e-9   # version1
V = np.linspace(-1.5, 1.5, 1000)  # np
# V = np.linspace(-3, 0, 1000)  # np

light_source = LightSource(source_type="standard"
                           , version="AM1.5g"
                           , x=wl
                           , output_units="photon_flux_per_m"
                           , concentration=1
                           )
# light_source = LightSource(source_type='laser', x=wl, center=2000, linewidth=200, power=1000)
q = constants.q
vacuum_permittivity = constants.vacuum_permittivity
if __name__ == '__main__':
    print('T', T)
    print('vint', vint)
    print('V', V)
    print('wl', wl)
    # plt.plot(wl)
    # plt.show()
    # for srh in [0,1]:
    #     for rad in [0,1]:
    #         for aug in [0,1]:
    #             for sur in [0,1]:
    #                 for gen in [0,1]:
    #                     print(f'srh {srh} ', end='')
    #                     print(f'rad {rad} ', end='')
    #                     print(f'aug {aug} ', end='')
    #                     print(f'sur {sur} ', end='')
    #                     print(f'gen {gen} ', end='')
    #                     print('')
