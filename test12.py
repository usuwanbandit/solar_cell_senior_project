from solcore import si, material
from solcore.structure import Layer, Structure, Junction, SolcoreMaterialToStr
from solcore.solar_cell import SolarCell
import solcore.quantum_mechanics as QM
import solcore.poisson_drift_diffusion as PDD
from solcore.quantum_mechanics.high_level_kp_QW import schrodinger
from solcore.quantum_mechanics.kp_bulk import KPbands
import pickle
import numpy as np
from solcore.state import State
import mpld3
from matplotlib import pyplot as plt, cm, ticker
# from material_of_InSb_GaSb import *
from solcore.solar_cell_solver import solar_cell_solver
import time

import matplotlib.pyplot as plt
from solcore.light_source import LightSource
from solcore.solar_cell_solver import solar_cell_solver
import numpy as np
from solcore.light_source import LightSource
data_solar_cell = dict(
    T=None,
    absorbed=None,
    short_circuit_data=None,
    pdd_data=None,
    recombination_currents=None,
    equilibrium_data=None,
    iv=None,
    qe=None,
    offset=0,
    note='note',
    list_structure=[],
    x_axis=[],
    x_axis_name='None',
    mode='None',
)

def get_color(number_of_color, darkness=0.5):
    cmap = plt.get_cmap('RdYlBu')
    colors = [cmap(i / number_of_color) for i in range(number_of_color)]

    # Darken the colors
    darkened_colors = [(darkness * r, darkness * g, darkness * b, a) for r, g, b, a in colors]

    return darkened_colors

h = 6.62607015e-34  # Planck constant in m^2 kg / s
c = 299792458  # Speed of light in m/s
eV_to_J = 1.60218e-19  # Conversion factor from eV to J
# ev = np.linspace(0.15, 3.54, 1000) * eV_to_J
T=300
vint = np.linspace(-3, 3, 1000)
# wl = h * c / ev
wl = np.linspace(350, 1200, 400) *1e-9
V = np.linspace(-2, 0, 200)  # np
# V = np.linspace(-3, 0, 1000)  # np

light_source = LightSource(source_type="standard"
                           , version="AM1.5g"
                           , x=wl
                           , output_units="photon_flux_per_m"
                           , concentration=1
                           )


def get_GaAs(T):
    n_GaAs_window = material("GaAs")(T=T, Nd=si('4e18 cm-3'))
    n_AlInP = material("AlInP")(T=T, Al=0.42, Nd=si('3e17 cm-3'))
    n_GaAs = material("GaAs")(T=T, Nd=si("2e18 cm-3"))
    p_GaAs = material("GaAs")(T=T, Na=si("5e16 cm-3"))
    p_GaInP = material("GaInP")(T=T, In=0.35, Na=si("2e18 cm-3"))
    p_GaAs_buffer = material("GaAs")(T=T, Na=si("2e18 cm-3"))
    p_GaAs_sub = material('GaAs')(T=T, Na=si('2e17 cm-3'))
    # layer

    GaAs_junction = Junction([
        Layer(width=si("300 nm"), material=n_GaAs_window, role="front_contact"),
        # Layer(width=si("30 nm"), material=n_AlInP, role="window"),
        Layer(width=si("100 nm"), material=n_GaAs, role="Emitter"),
        Layer(width=si("2800 nm"), material=p_GaAs, role="Base"),
        # Layer(width=si("100 nm"), material=p_GaInP, role="BSF"),
        # Layer(width=si("150 nm"), material=p_GaAs_buffer, role="Buffer"),

    ],
        T=T, kind="PDD", )
    my_solar_cell = SolarCell([

        GaAs_junction,

    ]
        , T=T, substrate=p_GaAs_sub, )
    return my_solar_cell

def defultsaveing(solarcell, saveaddrest):
    saveaddrest["T"] = solarcell.T
    saveaddrest['absorbed'] = solarcell.absorbed
    saveaddrest['short_circuit_data'] = solarcell[0].short_circuit_data.copy()
    saveaddrest['pdd_data'] = solarcell[0].pdd_data.copy()
    saveaddrest['recombination_currents'] = solarcell[0].recombination_currents.copy()
    saveaddrest['equilibrium_data'] = solarcell[0].equilibrium_data.copy()
    saveaddrest['iv'] = solarcell.iv.copy()
    saveaddrest['offset'] = solarcell[0].offset
    saveaddrest['qe'] = solarcell[0].qe.copy()

    return saveaddrest

def savecell(cell):
    solar_cell_solver(cell, "qe",
                      user_options={"light_source": light_source,
                                    "wavelength": wl,
                                    "optics_method": "TMM",
                                    }, )
    # IV
    solar_cell_solver(cell, "iv"
                      , user_options={"light_source": light_source,
                                      "wavelength": wl,
                                      "optics_method": None,
                                      "light_iv": True,
                                      "mpp": True,
                                      "voltages": V,
                                      "internal_voltages": vint,
                                      }, )
    return cell

def simulation0D_sun_constant(cell_list, condition):
    set_of_data = []
    for mode, cell in cell_list.items():
        data_mode = data_solar_cell.copy()
        data_mode['mode'] = mode
        data_mode['x_axis'] = condition

        cell = savecell(cell)
        data_mode = defultsaveing(cell, data_mode, )
        print(data_mode["iv"]["Pmpp"])
        print(data_mode["iv"]["Isc"])
        print(data_mode["iv"]["Voc"])
        print(data_mode["iv"]["FF"])
        print(data_mode["mode"])
        print('finite')
        set_of_data.append(data_mode)
    return set_of_data

def save_set_of_data_sun_constant(set_of_data, version, focus_area=None):
    if focus_area is None:
        focus_area = (50, 650)
    simpifly = None
    fig, ax1 = plt.subplots(1, 1, figsize=(6, 4))
    fig_5, ax1_5 = plt.subplots(1, 1, figsize=(6, 4))
    fig1, axes = plt.subplots(2, 2, figsize=(11.25, 8))
    fig2, axIV = plt.subplots(1, 1, figsize=(8, 6))
    # fig2_5, axJ = plt.subplots(1, 1, figsize=(8, 6))
    fig3, axCar = plt.subplots(len(set_of_data), 1, figsize=(16, 5 * len(set_of_data)))
    fig3_5, axCar2 = plt.subplots(len(set_of_data), 1, figsize=(16, 5 * len(set_of_data)))
    fig_b1, band1 = plt.subplots(len(set_of_data), 1, figsize=(16, 5 * len(set_of_data)))
    fig_b2, band2 = plt.subplots(len(set_of_data), 1, figsize=(16, 5 * len(set_of_data)))
    if len(set_of_data) > 5:
        simpifly = np.linspace(0, len(set_of_data), 5)
        simpifly = [int(i) for i in simpifly].append(len(set_of_data) - 1)
    Pmpp = []
    Isc = []
    Voc = []
    FF = []
    skip = 0
    count = 0
    color1 = get_color(len(set_of_data), darkness=0.9)
    for num, data in enumerate(set_of_data):

        print(f'loading {data["mode"]} num = {num}')
        ax1.plot(data['qe']["WL"] * 1e9, data["qe"]["EQE"], label=f"{data['mode']}", color=color1[count])
        ax1.legend(loc="upper right", frameon=False)
        ax1.set_xlabel("Wavelength (nm)")
        ax1.set_ylabel("EQE")
        ax1.set_ylim(0, 1.1)
        ax1.set_xlim(350, 1000)
        ax1.legend()
        # plt.tight_layout()
        fig1.suptitle(f"{version}")

        ax1_5.semilogy(data['qe']["WL"] * 1e9, data["qe"]["EQE"], label=f"{data['mode']}", color=color1[count])
        ax1_5.legend(loc="upper right", frameon=True)
        ax1_5.set_xlabel("Wavelength (nm)")
        ax1_5.set_ylabel("EQE")
        ax1_5.set_ylim(1e-6, 1)
        ax1_5.set_xlim(900, max(wl)*1e9)
        ax1_5.legend()
        fig_5.suptitle(f"{version}")
        count += 1
        linestyle = ["-", "--", ":", "-.", ]
        # marker = [".", ",", "o", 'v', "^", "<", ">", "s", "p", "*", "h", "+", "x", "D", "d"]
        color = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black', 'orange', 'purple']
        Pmpp.append(data["iv"]["Pmpp"])
        Isc.append(data["iv"]["Isc"])
        Voc.append(data["iv"]["Voc"])
        FF.append(data["iv"]["FF"])
        if simpifly is None:
            # axIV.plot(-data["iv"]["IV"][0], data["iv"]["IV"][1] / -10, label=f"{data['mode']}")
            # axIV.plot(abs(data["iv"]["IV"][0]), abs(data["iv"]["IV"][1] / 10), label=f"{data['mode']}")
            axIV.plot(-data["iv"]["IV"][0], data["iv"]["IV"][1] / -10, label=f"{data['mode']}")

            # try:
            #
            #     axJ.semilogy(abs(data["iv"]["IV"][0], data["iv"]["IV"][1]), label=f"J{data['mode']}", color=color[num], linestyle=linestyle[0])
            #     axJ.semilogy(abs(V), data['recombination_currents']['Jrad'], color=color[num],linestyle=linestyle[1])
            #     axJ.semilogy(abs(V), data['recombination_currents']['Jsrh'], color=color[num],linestyle=linestyle[2])
            #     axJ.semilogy(abs(V), data['recombination_currents']['Jsur'], color=color[num],linestyle=linestyle[3])
            #     axJ.semilogy(abs(V), data['recombination_currents']['Jaug'], color=color[num],linestyle='-.', dashes=(5, 2, 1, 1, 1, 2))
            # except:
            #     pass

        elif num in simpifly:
            # axIV.plot(-data["iv"]["IV"][0], data["iv"]["IV"][1] / -10, label=f"{data['mode']}")
            # axIV.plot(abs(data["iv"]["IV"][0]), abs(data["iv"]["IV"][1] / 10), label=f"{data['mode']}")
            axIV.plot(-data["iv"]["IV"][0], data["iv"]["IV"][1] / -10, label=f"{data['mode']}")

            # try:
            #     # axJ.semilogy(-data["iv"]["IV"][0], abs(data["iv"]["IV"][1]), label=f"J{data['mode']}", color=color[num], linestyle=linestyle[0])
            #     # axJ.semilogy(-V, abs(data['recombination_currents']['Jrad']), color=color[num],linestyle=linestyle[1])
            #     # axJ.semilogy(-V, abs(data['recombination_currents']['Jsrh']), color=color[num],linestyle=linestyle[2])
            #     # axJ.semilogy(-V, abs(data['recombination_currents']['Jsur']), color=color[num],linestyle=linestyle[3])
            #     # axJ.semilogy(-V, abs(data['recombination_currents']['Jaug']), color=color[num], linestyle='-.', dashes=(5, 2, 1, 1, 1, 2))
            #
            #     axJ.semilogy(abs(data["iv"]["IV"][0]), abs(data["iv"]["IV"][1]), label=f"J{data['mode']}", color=color[num],linestyle=linestyle[0])
            #     axJ.semilogy(abs(V), abs(data['recombination_currents']['Jrad']), color=color[num], linestyle=linestyle[1])
            #     axJ.semilogy(abs(V), abs(data['recombination_currents']['Jsrh']), color=color[num], linestyle=linestyle[2])
            #     axJ.semilogy(abs(V), abs(data['recombination_currents']['Jsur']), color=color[num], linestyle=linestyle[3])
            #     axJ.semilogy(abs(V), abs(data['recombination_currents']['Jaug']), color=color[num], linestyle='-.', dashes=(5, 2, 1, 1, 1, 2))
            #
            #
            # except:
            #     pass
        axIV.set_ylim(0, 30)
        axIV.set_xlim(-0.1, 1.5)
        axIV.set_xlabel("Voltage (V)")
        axIV.set_ylabel("J$_{SC}$ (mA/cm$^{2}$)")
        axIV.legend()

        # axJ.set_xlabel("Voltage (V)")
        # axJ.set_ylabel("J$_{SC}$ (A/m$^{2}$)")
        # axJ.set_ylim(1e-4, 1e5)
        #
        # axJ.legend()
        # plt.tight_layout()

        try:
            xsc = data["short_circuit_data"]['Bandstructure']['x'] + data['offset']
            nsc = data["short_circuit_data"]['Bandstructure']['n']
            psc = data["short_circuit_data"]['Bandstructure']['p']
            xeq = data["equilibrium_data"]['Bandstructure']['x'] + data['offset']
            neq = data["equilibrium_data"]['Bandstructure']['n']
            peq = data["equilibrium_data"]['Bandstructure']['p']
            # axCar[num].set_title(data["mode"])
            axCar[num].semilogy(xsc * 1e9, nsc, 'b', label='e @ short circuit')
            axCar[num].semilogy(xsc * 1e9, psc, 'r', label='h @ short circuit')
            axCar[num].semilogy(xeq * 1e9, neq, 'b--', label='e @ equilibrium')
            axCar[num].semilogy(xeq * 1e9, peq, 'r--', label='h @ equilibrium')

            axCar[num].set_xlabel('Position (nm)')
            axCar[num].set_ylabel('Carrier density (m$^{-3}$)')
            # axCar[num].set_ylim(1e6, 1e25)
            axCar[num].legend()
            # axCar2[num].set_title(data["mode"])
            axCar2[num].semilogy(xsc * 1e9, nsc, 'b', label='e @ short circuit')
            axCar2[num].semilogy(xsc * 1e9, psc, 'r', label='h @ short circuit')
            axCar2[num].semilogy(xeq * 1e9, neq, 'b--', label='e @ equilibrium')
            axCar2[num].semilogy(xeq * 1e9, peq, 'r--', label='h @ equilibrium')
            axCar2[num].set_xlabel('Position (nm)')
            axCar2[num].set_ylabel('Carrier density (m$^{-3}$)')
            axCar2[num].legend()
            axCar2[num].set_xlim(focus_area)
            # axCar2[num].set_ylim(1e6, 1e25)


        except:
            print("something wrong with carrier distribution")
            pass
        try:
            x = data['pdd_data']['positive_V']['Bandstructure']['x']
            Ec = data['pdd_data']['positive_V']['Bandstructure']['Ec']
            Ev = data['pdd_data']['positive_V']['Bandstructure']['Ev']
            Efc = data['pdd_data']['positive_V']['Bandstructure']['Efe']
            Efh = data['pdd_data']['positive_V']['Bandstructure']['Efh']
            potential = data['pdd_data']['positive_V']['Bandstructure']['potential']

            # band1[num].set_title(data["mode"])
            band1[num].plot(x * 1e9, Ec, 'b', label="Ec")
            band1[num].plot(x * 1e9, Ev, 'r', label="Ev")
            # band1[num].plot(x * 1e9, Efc, 'b--', label="Efe")
            # band1[num].plot(x * 1e9, Efh, 'r--', label="Efh")
            # band1[num].plot(x * 1e9, potential, label="potential")
            band1[num].set_xlabel('Position (nm)')
            band1[num].set_ylabel('Energy (eV)')
            band1[num].legend()

            # band2[num].set_title(data["mode"])
            band2[num].plot(x * 1e9, Ec, 'b', label="Ec")
            band2[num].plot(x * 1e9, Ev, 'r', label="Ev")
            # band2[num].plot(x * 1e9, Efc, 'b--', label="Efe")
            # band2[num].plot(x * 1e9, Efh, 'r--', label="Efh")
            # band2[num].plot(x * 1e9, potential, label="potential")
            band2[num].set_xlabel('Position (nm)')
            band2[num].set_ylabel('Energy (eV)')
            band2[num].legend()
            band2[num].set_xlim(focus_area)

        except Exception as error:
            print(f'error is {error}')


    axes[0, 0].plot(set_of_data[0]['x_axis'], np.array(Pmpp) / 10, color='r', marker='o',)
    axes[0, 0].set_xlabel(set_of_data[0]['x_axis_name'])
    axes[0, 0].set_ylabel("Efficiency (%)")

    axes[0, 1].semilogy(set_of_data[0]['x_axis'], abs(np.array(Isc)), color='g', marker='o',)
    axes[0, 1].set_xlabel(set_of_data[0]['x_axis_name'])
    axes[0, 1].set_ylabel("I$_{SC}$ (Am$^{-2}$)")

    axes[1, 0].plot(set_of_data[0]['x_axis'], abs(np.array(Voc)), color='b', marker='o',)
    axes[1, 0].set_xlabel(set_of_data[0]['x_axis_name'])
    axes[1, 0].set_ylabel("V$_{OC}$ (V)")

    axes[1, 1].plot(set_of_data[0]['x_axis'], abs(np.array(FF)) * 100, color='k', marker='o',)
    axes[1, 1].set_xlabel(set_of_data[0]['x_axis_name'])
    axes[1, 1].set_ylabel("Fill Factor (%)")

    fig.suptitle(f"EQE of  {version}")
    fig_5.suptitle(f"Zoom EQE of {version}")
    fig2.suptitle(f'IV of {version}')
    # fig2_5.suptitle(f'current of {version} Jtotle - Jrad-- Jsch : Jsur-. Jaug-..' )
    fig3.suptitle(f"Carrier distribution of {version}")
    fig3_5.suptitle(f"Zoom Carrier distribution of {version}")
    fig_b1.suptitle(f"band gap of {version}")
    fig_b2.suptitle(f"Zoom band gap of {version}")
    try:
        fig1.suptitle(f'performance of {set_of_data[0]["x_axis_txt"]}')
        axes[0,0].set_xticks([])  # Remove x-axis ticks
        axes[0,1].set_xticks([])  # Remove x-axis ticks
        axes[1,0].set_xticks([])  # Remove x-axis ticks
        axes[1,1].set_xticks([])  # Remove x-axis ticks
    except:
        fig1.suptitle(f'performance of {version}')
    plt.tight_layout()
    fig1.tight_layout()
    fig_5.tight_layout()
    fig2.tight_layout()
    # fig2_5.tight_layout()
    fig3.tight_layout()
    fig3_5.tight_layout()
    fig_b1.tight_layout()
    fig_b2.tight_layout()
    plt.tight_layout()

    print('save complete')

Templist = [300, 350]
cell_list = {}
for i in Templist:
    cell = get_GaAs(i)
    cell_list[f"temp {i}"]= cell
set_of_data = simulation0D_sun_constant(cell_list, Templist)
save_set_of_data_sun_constant(set_of_data, 'temp')

plt.show()

