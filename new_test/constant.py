import matplotlib.pyplot as plt
import numpy as np
from solcore import constants
from solcore.light_source import LightSource
# import matplotlib.pyplot as plt
h = 6.62607015e-34  # Planck constant in m^2 kg / s
c = 299792458  # Speed of light in m/s
eV_to_J = 1.60218e-19  # Conversion factor from eV to J
# ev = np.linspace(0.15, 3.54, 1000) * eV_to_J
T=300
vint = np.linspace(-6, 6, 1000)
# wl = h * c / ev

wl = np.linspace(350, 6000, 2000) *1e-9
V = np.linspace(-3, 3, 1000)  # np
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
    # print('T', T)
    # print('vint', vint)
    # print('V', V)
    # print('wl', wl)
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
    A11= [0, 0.5,0.85, 1.35, 1.95, 3.45, 3.95]
    V11= [7, 100, 160, 240, 320, 400, 480]
    plt.plot(A11,V11, label="Armature voltage(V)")
    plt.xlabel("Field current(A)")
    # plt.ylabel("Armature voltage(V)")
    # plt.legend
    # plt.show()
    A12 = [0, 0.42, 0.7, 1.3, 1.6, 2, 2.4]
    A22 = np.array([0, 0.08, 0.16, 0.24, 0.32, 0.4, 0.48])*1000
    plt.plot(A12,A22, label="Short circuit current (mA)")

    # V1 = [400, 410, 425, 435, 450, 460]
    # A2 = [0.48, 0.4, 0.32, 0.24, 0.16, 0]
    # plt.plot(A2, V1)
    # plt.ylabel("Armature Voltage(V)")
    # plt.xlabel("Armature current(A)")
    # plt.ylim(300, 500)
    # plt.xlim(0, 0.5)
    plt.title("Field current - Armature volt and short cir current")

    plt.legend()
    # plt.title("Armature Voltage - Armature current at@(field current 4.3A)")
    plt.show()