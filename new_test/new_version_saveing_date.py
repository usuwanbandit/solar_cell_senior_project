import numpy as np
from solcore.state import State
import mpld3
from matplotlib import pyplot as plt, cm, ticker
# from material_of_InSb_GaSb import *
from material_and_layer_QD import *
from lib_save_file import *
from solcore.solar_cell_solver import solar_cell_solver
import time
from constant import *
import tkinter as tk

# vint = np.linspace(-3, 3, 600)
# V = np.linspace(-1.5, 0, 300)  # np

# wl = np.linspace(350, 3000, 1001) * 1e-9  # version1
# light_source = LightSource(source_type="standard"
#                            , version="AM1.5g"
#                            , x=wl
#                            , output_units="photon_flux_per_m"
#                            , concentration=1
#                            )
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
def defultsaveing(solarcell, saveaddrest, version, save=True):
    saveaddrest["T"] = solarcell.T
    saveaddrest['absorbed'] = solarcell.absorbed
    saveaddrest['short_circuit_data'] = solarcell[0].short_circuit_data.copy()
    saveaddrest['pdd_data'] = solarcell[0].pdd_data.copy()
    saveaddrest['recombination_currents'] = solarcell[0].recombination_currents.copy()
    saveaddrest['equilibrium_data'] = solarcell[0].equilibrium_data.copy()
    saveaddrest['iv'] = solarcell.iv.copy()
    saveaddrest['offset'] = solarcell[0].offset
    saveaddrest['qe'] = solarcell[0].qe.copy()
    if save:
        with open(f'{version}.pkl', 'wb') as fin:
            pickle.dump(saveaddrest, fin)
            print('dictionary saved successfully to file')
    return saveaddrest


def load_old_data(version):
    with open(f'{version}', 'rb') as fp:
        data = pickle.load(fp)
    print('Loading dictionary complete')
    # print(data["allI"])
    return data


def save_set_of_data_sun_constant(set_of_data, version, focus_area=None):
    if focus_area is None:
        focus_area = (50, 650)
    simpifly = None
    fig, ax1 = plt.subplots(1, 1, figsize=(6, 4))
    fig_5, ax1_5 = plt.subplots(1, 1, figsize=(12, 8))
    fig_6, ax1_6 = plt.subplots(1, 1, figsize=(12, 8))
    fig1, axes = plt.subplots(2, 2, figsize=(11.25, 8))
    fig2, axIV = plt.subplots(1, 1, figsize=(8, 6))
    fig2_1, axJ = plt.subplots(1, 1, figsize=(8, 6))
    fig2_2, axJrad = plt.subplots(1, 1, figsize=(8, 6))
    fig2_3, axJsrh = plt.subplots(1, 1, figsize=(8, 6))
    fig2_4, axJaug = plt.subplots(1, 1, figsize=(8, 6))
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
    delete_point = []
    skip = 0
    count = 0
    color1 = get_color(len(set_of_data), darkness=0.9)
    for num, data in enumerate(set_of_data):
        # if np.any(data["qe"]["EQE"] < 0) or np.any(data["qe"]["EQE"] > 101)  or data["iv"]["Voc"] == -1.5:
        #     delete_point.append(num)
        #     continue


        print(f'loading {data["mode"]} num = {num}')
        ax1.plot(data['qe']["WL"] * 1e9, data["qe"]["EQE"], label=f"{data['mode']}", color=color1[count])
        ax1.legend(loc="upper right", frameon=False)
        ax1.set_xlabel("Wavelength (nm)")
        ax1.set_ylabel("EQE")
        ax1.set_ylim(0, 1.1)
        ax1.set_xlim(350, 1000)
        ax1.legend()
        plt.tight_layout()
        fig1.suptitle(f"{version}")

        ax1_5.semilogy(data['qe']["WL"] * 1e9, data["qe"]["EQE"], label=f"{data['mode']}", color=color1[count])
        ax1_5.legend(loc="upper right", frameon=True)
        ax1_5.set_xlabel("Wavelength (nm)")
        ax1_5.set_ylabel("EQE")
        ax1_5.set_ylim(1e-6, 1)
        ax1_5.set_xlim(900, max(wl)*1e9)
        ax1_5.legend()
        fig_5.suptitle(f"{version}")

        ax1_6.plot(data['qe']["WL"] * 1e9, data["qe"]["EQE"], label=f"{data['mode']}", color=color1[count])
        ax1_6.legend(loc="upper right", frameon=True)
        ax1_6.set_xlabel("Wavelength (nm)")
        ax1_6.set_ylabel("EQE")
        ax1_6.set_ylim(-1,1)
        ax1_6.set_xlim(900, max(wl) * 1e9)
        ax1_6.legend()
        fig_6.suptitle(f"{version}")
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

            try:

                axJ.semilogy(abs(data["iv"]["IV"][0], data["iv"]["IV"][1]), label=f"J{data['mode']}", color=color[num], linestyle=linestyle[0])
                axJrad.semilogy(abs(V), data['recombination_currents']['Jrad'], color=color[num],linestyle=linestyle[1])
                axJsrh.semilogy(abs(V), data['recombination_currents']['Jsrh'], color=color[num],linestyle=linestyle[2])
                # axJ.semilogy(abs(V), data['recombination_currents']['Jsur'], color=color[num],linestyle=linestyle[3])
                axJaug.semilogy(abs(V), data['recombination_currents']['Jaug'], color=color[num],linestyle=linestyle[3])
            except:
                pass

        elif num in simpifly:
            # axIV.plot(-data["iv"]["IV"][0], data["iv"]["IV"][1] / -10, label=f"{data['mode']}")
            # axIV.plot(abs(data["iv"]["IV"][0]), abs(data["iv"]["IV"][1] / 10), label=f"{data['mode']}")
            axIV.plot(-data["iv"]["IV"][0], data["iv"]["IV"][1] / -10, label=f"{data['mode']}")

            try:
                # axJ.semilogy(-data["iv"]["IV"][0], abs(data["iv"]["IV"][1]), label=f"J{data['mode']}", color=color[num], linestyle=linestyle[0])
                # axJ.semilogy(-V, abs(data['recombination_currents']['Jrad']), color=color[num],linestyle=linestyle[1])
                # axJ.semilogy(-V, abs(data['recombination_currents']['Jsrh']), color=color[num],linestyle=linestyle[2])
                # axJ.semilogy(-V, abs(data['recombination_currents']['Jsur']), color=color[num],linestyle=linestyle[3])
                # axJ.semilogy(-V, abs(data['recombination_currents']['Jaug']), color=color[num], linestyle='-.', dashes=(5, 2, 1, 1, 1, 2))

                axJ.semilogy(abs(data["iv"]["IV"][0]), abs(data["iv"]["IV"][1]), label=f"J{data['mode']}", color=color[num],linestyle=linestyle[0])
                axJrad.semilogy(abs(V), abs(data['recombination_currents']['Jrad']), color=color[num], linestyle=linestyle[1])
                axJsrh.semilogy(abs(V), abs(data['recombination_currents']['Jsrh']), color=color[num], linestyle=linestyle[2])
                # axJ.semilogy(abs(V), abs(data['recombination_currents']['Jsur']), color=color[num], linestyle=linestyle[3])
                axJaug.semilogy(abs(V), abs(data['recombination_currents']['Jaug']), color=color[num], linestyle=linestyle[3])


            except:
                pass
        axIV.set_ylim(-30, 30)
        axIV.set_xlim(-1.5, 1.5)
        axIV.set_xlabel("Voltage (V)")
        axIV.set_ylabel("J$_{SC}$ (mA/cm$^{2}$)")
        axIV.legend()
        # plt.tight_layout()

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
            axCar[num].set_title(data["mode"])
            axCar[num].semilogy(xsc * 1e9, nsc, 'b', label='e @ short circuit')
            axCar[num].semilogy(xsc * 1e9, psc, 'r', label='h @ short circuit')
            axCar[num].semilogy(xeq * 1e9, neq, 'b--', label='e @ equilibrium')
            axCar[num].semilogy(xeq * 1e9, peq, 'r--', label='h @ equilibrium')

            axCar[num].set_xlabel('Position (nm)')
            axCar[num].set_ylabel('Carrier density (m$^{-3}$)')
            axCar[num].set_ylim(1e6, 1e25)
            axCar[num].legend()
            axCar2[num].set_title(data["mode"])
            axCar2[num].semilogy(xsc * 1e9, nsc, 'b', label='e @ short circuit')
            axCar2[num].semilogy(xsc * 1e9, psc, 'r', label='h @ short circuit')
            axCar2[num].semilogy(xeq * 1e9, neq, 'b--', label='e @ equilibrium')
            axCar2[num].semilogy(xeq * 1e9, peq, 'r--', label='h @ equilibrium')
            axCar2[num].set_xlabel('Position (nm)')
            axCar2[num].set_ylabel('Carrier density (m$^{-3}$)')
            axCar2[num].legend()
            axCar2[num].set_xlim(focus_area)
            axCar2[num].set_ylim(1e6, 1e25)

            # plt.tight_layout()

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

            band1[num].set_title(data["mode"])
            band1[num].plot(x * 1e9, Ec, 'b', label="Ec")
            band1[num].plot(x * 1e9, Ev, 'r', label="Ev")
            # band1[num].plot(x * 1e9, Efc, 'b--', label="Efe")
            # band1[num].plot(x * 1e9, Efh, 'r--', label="Efh")
            # band1[num].plot(x * 1e9, potential, label="potential")
            band1[num].set_xlabel('Position (nm)')
            band1[num].set_ylabel('Energy (eV)')
            band1[num].legend()

            band2[num].set_title(data["mode"])
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
    print(delete_point)

    if len(delete_point) > 0:
        mask = np.ones(len(set_of_data[0]['x_axis']), dtype=bool)
        mask[delete_point] = False
        x_axis = np.array(set_of_data[0]['x_axis'])[mask]
    else:
        x_axis = np.array(set_of_data[0]['x_axis'])

    print(Pmpp)
    print(Isc)
    print(Voc)
    print(FF)
    print(x_axis)
    print(delete_point)
    # color = [plt.cm.hsv(i / len(set_of_data)) for i in range(len(set_of_data))]
    # axes.text(0.95, 0.95, 'Sample Text', ha='right', va='top', transform=plt.gca().transAxes, fontsize=12)
    # print(Pmpp)
    axes[0, 0].plot(x_axis[:len(set_of_data)], np.array(Pmpp) / 10, color='r', marker='o',)
    axes[0, 0].set_xlabel(set_of_data[0]['x_axis_name'])
    axes[0, 0].set_ylabel("Efficiency (%)")

    axes[0, 1].semilogy(x_axis[:len(set_of_data)], abs(np.array(Isc)), color='g', marker='o',)
    axes[0, 1].set_xlabel(set_of_data[0]['x_axis_name'])
    axes[0, 1].set_ylabel("I$_{SC}$ (Am$^{-2}$)")

    axes[1, 0].plot(x_axis[:len(set_of_data)], abs(np.array(Voc)), color='b', marker='o',)
    axes[1, 0].set_xlabel(set_of_data[0]['x_axis_name'])
    axes[1, 0].set_ylabel("V$_{OC}$ (V)")

    axes[1, 1].plot(x_axis[:len(set_of_data)], abs(np.array(FF)) * 100, color='k', marker='o',)
    axes[1, 1].set_xlabel(set_of_data[0]['x_axis_name'])
    axes[1, 1].set_ylabel("Fill Factor (%)")

    fig.suptitle(f"EQE of  {version}")
    fig_5.suptitle(f"Zoom EQE of {version}")
    fig_6.suptitle(f"Check EQE of {version}")
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
    # fig1.legend()
    # plt.legend()

    fig.savefig(f'EQE_{version}.png', dpi=300)
    fig_5.savefig(f'EQE_{version}_zoom.png', dpi=300)
    fig_6.savefig(f'EQE_{version}_Check.png', dpi=300)
    fig1.savefig(f'performance_{version}.png', dpi=300)
    fig2.savefig(f'IV_curve_{version}.png', dpi=300)
    fig2_1.savefig(f'current_curve_{version}.png', dpi=300)
    fig2_2.savefig(f'radiative_recombination_current_{version}.png', dpi=300)
    fig2_3.savefig(f'SRH_current_{version}.png', dpi=300)
    fig2_4.savefig(f'Auger_current_{version}.png', dpi=300)

    mpld3.save_html(fig3, f'Carrier_distribution_{version}.html')
    mpld3.save_html(fig3_5, f'Carrier_distribution_{version}_zoom.html')
    mpld3.save_html(fig_b1, f'Band_diagramming_of_{version}.html')
    mpld3.save_html(fig_b2, f'Band_diagramming_of_{version}_zoom.html')

    save_file_direction(f'{version}', f'{version}', saveing_data=set_of_data)

    movefile(f'IV_curve_{version}.png', f'{version}')
    movefile(f'EQE_{version}_Check.png', f"{version}")
    # movefile(f'current_curve_{version}.png', f'{version}')
    movefile(f'performance_{version}.png', f'{version}')
    movefile(f'EQE_{version}_zoom.png', f'{version}')
    movefile(f'EQE_{version}.png', f'{version}')
    # movefile(f'carrier_distribution{version}.html', f'{version}')

    # movefile
    print('save complete')


def simulation1D_sun_constant(version, sim_mat, plot_note, pdd_options=None, note='', old_data=None ):
    if pdd_options == None:
        pdd_options = State()

        # pdd_options.recalculate_absorption = True

        # Mesh control
        pdd_options.meshpoints = -400
        pdd_options.growth_rate = 0.7
        pdd_options.coarse = 20e-9
        pdd_options.fine = 1e-9
        pdd_options.ultrafine = 0.2e-9

        # Convergence control
        pdd_options.clamp = 20
        pdd_options.nitermax = 100
        pdd_options.ATol = 1e-14
        pdd_options.RTol = 1e-6

        # Recombination control
        pdd_options.srh = 1
        pdd_options.rad = 1
        pdd_options.aug = 0
        pdd_options.sur = 1
        pdd_options.gen = 0
    else:
        pass
    # print('pdd_options.recalculate_absorption', pdd_options.recalculate_absorption)
    print('pdd_options.meshpoints',pdd_options.meshpoints)
    print('pdd_options.growth_rate',pdd_options.growth_rate)
    print('pdd_options.coarse',pdd_options.coarse)
    print('pdd_options.fine',pdd_options.fine)
    print('pdd_options.ultrafine',pdd_options.ultrafine)
    print('pdd_options.clamp',pdd_options.clamp)
    print('pdd_options.nitermax',pdd_options.nitermax)
    print('pdd_options.RTol',pdd_options.RTol)
    print('pdd_options.ATol',pdd_options.ATol)
    print('pdd_options.RTol',pdd_options.RTol)
    print('pdd_options.srh',pdd_options.srh)
    print('pdd_options.rad',pdd_options.rad)
    print('pdd_options.aug',pdd_options.aug)
    print('pdd_options.sur',pdd_options.sur)
    print('pdd_options.gen',pdd_options.gen)

    set_of_data = []
    if old_data != None:
        set_of_data = load_old_data(f'{old_data}.pkl')
        continue_sim = len(set_of_data)
        print(continue_sim)
    else:
        continue_sim = -1
    counting = 0
    for mode, cell in sim_mat.items():
        if continue_sim >= counting: #skip index
            print("skipping", mode)
            counting += 1
            continue
        counting += 1
        data_mode = data_solar_cell.copy()
        data_mode['mode'] = mode
        data_mode['note'] = note
        data_mode['x_axis'] = plot_note['x_axis']
        data_mode['x_axis_name'] = plot_note["x_axis_name"]
        try:
            data_mode['x_axis_txt'] = plot_note["x_axis_txt"]
        except:pass
        data_mode['list_structure'].append(
            "start item ================================================================================")
        _ = [data_mode['list_structure'].append(str(i)) for i in cell]
        data_mode['list_structure'].append(
            "end item   ================================================================================")
        print(data_mode['mode'])
        cell = savecell(cell, pdd_options)
        data_mode = defultsaveing(cell, data_mode, version)
        print(data_mode["iv"]["Pmpp"])
        print(data_mode["iv"]["Isc"])
        print(data_mode["iv"]["Voc"])
        print(data_mode["iv"]["FF"])
        set_of_data.append(data_mode)
        back_up_data(set_of_data, version)
    return set_of_data

def simulation0D_sun_constant(version, cell, plot_note, pdd_options=None, note='', mode="None"):
    if pdd_options == None:
        pdd_options = State()

        # pdd_options.recalculate_absorption = True

        # Mesh control
        pdd_options.meshpoints = -400
        pdd_options.growth_rate = 0.7
        pdd_options.coarse = 20e-9
        pdd_options.fine = 1e-9
        pdd_options.ultrafine = 0.2e-9

        # Convergence control
        pdd_options.clamp = 20
        pdd_options.nitermax = 100
        pdd_options.ATol = 1e-14
        pdd_options.RTol = 1e-6

        # Recombination control
        pdd_options.srh = 1
        pdd_options.rad = 1
        pdd_options.aug = 0
        pdd_options.sur = 1
        pdd_options.gen = 0
    else:
        pass
    # print('pdd_options.recalculate_absorption', pdd_options.recalculate_absorption)
    print('pdd_options.meshpoints',pdd_options.meshpoints)
    print('pdd_options.growth_rate',pdd_options.growth_rate)
    print('pdd_options.coarse',pdd_options.coarse)
    print('pdd_options.fine',pdd_options.fine)
    print('pdd_options.ultrafine',pdd_options.ultrafine)
    print('pdd_options.clamp',pdd_options.clamp)
    print('pdd_options.nitermax',pdd_options.nitermax)
    # print('pdd_options.RTol',pdd_options.RTol)
    print('pdd_options.ATol',pdd_options.ATol)
    print('pdd_options.RTol',pdd_options.RTol)
    print('pdd_options.srh',pdd_options.srh)
    print('pdd_options.rad',pdd_options.rad)
    print('pdd_options.aug',pdd_options.aug)
    print('pdd_options.sur',pdd_options.sur)
    print('pdd_options.gen',pdd_options.gen)

    set_of_data = []

    data_mode = data_solar_cell.copy()
    data_mode['mode'] = mode
    data_mode['note'] = note
    data_mode['x_axis'] = plot_note['x_axis']
    data_mode['x_axis_name'] = plot_note["x_axis_name"]
    try:
        data_mode['x_axis_txt'] = plot_note["x_axis_txt"]
    except:pass
    data_mode['list_structure'].append(
        "start item ================================================================================")
    _ = [data_mode['list_structure'].append(str(i)) for i in cell]
    data_mode['list_structure'].append(
        "end item   ================================================================================")
    print(data_mode['mode'])
    cell = savecell(cell, pdd_options)
    data_mode = defultsaveing(cell, data_mode, version)
    print(data_mode["iv"]["Pmpp"])
    print(data_mode["iv"]["Isc"])
    print(data_mode["iv"]["Voc"])
    print(data_mode["iv"]["FF"])
    set_of_data.append(data_mode)
    back_up_data(set_of_data, version)
    return set_of_data


def savecell(cell, pdd_options):
    # offset = 0
    # pdd_options.position = []
    # for junction in cell:
    #     for layer in junction:
    #                 if layer.role is not None:
    #                     pdd_options.position.append(max(1e-10, layer.width / 5000))
    #                 else:
    #                     pdd_options.position.append(1e-11)
    #                 offset += layer.width
    # print(pdd_options.position)
    # print(len(pdd_options.position))
    solar_cell_solver(cell, "qe",
                      user_options={"light_source": light_source,
                                    "wavelength": wl,
                                    "optics_method": "TMM",
                                    "internal_voltages": vint,
                                    # "radiative_coupling": True,
                                    'recalculate_absorption': pdd_options.recalculate_absorption,
                                    # "position": pdd_options.position,
                                    "meshpoints": pdd_options.meshpoints,
                                    "growth_rate": pdd_options.growth_rate,
                                    "coarse": pdd_options.coarse,
                                    "fine": pdd_options.fine,
                                    "ultrafine": pdd_options.ultrafine,
                                    "clamp": pdd_options.clamp,
                                    'nitermax': pdd_options.nitermax,
                                    'ATol': pdd_options.ATol,
                                    "RTol": pdd_options.RTol,
                                    'srh': pdd_options.srh,
                                    'rad': pdd_options.rad,
                                    'aug': pdd_options.aug,
                                    'sur': pdd_options.sur,
                                    'gen': pdd_options.gen,
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
                                      # "radiative_coupling": True,
                                      # "position": pdd_options.position,
                                      "meshpoints": pdd_options.meshpoints,
                                      "growth_rate": pdd_options.growth_rate,
                                      "coarse": pdd_options.coarse,
                                      "fine": pdd_options.fine,
                                      "ultrafine": pdd_options.ultrafine,
                                      "clamp": pdd_options.clamp,
                                      'nitermax': pdd_options.nitermax,
                                      'ATol': pdd_options.ATol,
                                      "RTol": pdd_options.RTol,
                                      'srh': pdd_options.srh,
                                      'rad': pdd_options.rad,
                                      'aug': pdd_options.aug,
                                      'sur': pdd_options.sur,
                                      'gen': pdd_options.gen,
                                      }, )
    return cell

def sim1D_sun_constant(version, sim_mat, plot_note, note, pdd_options=None, old_data=None):  # sc = simulation at 1 sun
    start = time.perf_counter()
    # print([i for i in pdd_options.__dict__])
    # print(pdd_options.meshpoints)
    # print(pdd_options.growth_rate)
    # print(pdd_options.coarse)
    # print(pdd_options.fine)
    # print(pdd_options.ultrafine)
    # print(pdd_options.RTol)
    # print(pdd_options.clamp)
    set_of_data_sun_constant = simulation1D_sun_constant(version, sim_mat, plot_note, note=note,
                                                         pdd_options=pdd_options, old_data=old_data)
    stop = time.perf_counter()
    hours, minutes, seconds = sec_to_hms(stop - start)
    print(f"this run take time {hours} hours/ {minutes} minutes/ {seconds} seconds")
    # root = tk.Tk()
    # root.withdraw()
    save_set_of_data_sun_constant(set_of_data_sun_constant, version)
    # note_from_mat = dict(x_axis=list, x_axis_name="txt")
    try:
        movefile(f'Carrier_distribution_{version}.html', f'{version}')
        movefile(f'Carrier_distribution_{version}_zoom.html', f'{version}')
        movefile(f'Band_diagramming_of_{version}.html', f'{version}')
        movefile(f'Band_diagramming_of_{version}_zoom.html', f'{version}')
    except PermissionError as e:
        print(f"Error: {e}")
    # show_warning(f"this run take time {hours} hours/ {minutes} minutes/ {seconds} seconds")
    # root.update()
    # plt.show()


# SetMeshParameters(ultrafine=1e-10, growth_rate=0.8)

normal_operation = State()

normal_operation.meshpoints = -400
normal_operation.growth_rate = 0.5
normal_operation.coarse = 20e-9
normal_operation.fine = 1e-9
normal_operation.ultrafine = 0.2e-9

normal_operation.clamp = 20
normal_operation.nitermax = 1000
normal_operation.ATol = 1.5e-09
normal_operation.RTol = 1e-4

normal_operation.srh = 0
normal_operation.rad = 0
normal_operation.aug = 0
normal_operation.sur = 1
normal_operation.gen = 0

normal_operation.recalculate_absorption = True

#        Layer(width=si(f"{50} nm"), material=i_GaAs_barrier, role="well"),
#        Layer(width=si(f"{i} nm"), material=InSb, role="well"),
#        Layer(width=si(f"{50} nm"), material=i_GaAs, role="well"),
#        Layer(width=si(f"{size_GaSb} nm"), material=GaSb, role="well"),  # 5-20 nm
#        Layer(width=si(f"{50} nm"), material=i_GaAs_barrier, role="well"),
#         x4
# srh 0 rad 1 aug 1 sur 0 gen 1 ไม่ได้ที่ res 20 and 1300  -255789 too much
# srh 0 rad 0 aug 0 sur 0 gen 0 ได้แล้ว แต้ว้่่าต้องมี rad ด้วย
# srh 0 rad 1 aug 1 sur 0 gen 0  ไม่ได้ที่ res 21 and 1300 -0.636511E-1 ดีขึ้นค่าหลังไม่ค่อยแย่อยู่ที่ -72 QDSC_InSb_GaSb_sweep_InSb_pn
# srh 1 rad 1 aug 1 sur 0 gen 0  ไม่ได้ที่ res 21 and 1300 -0.636511E-1 เหมือนกับข้างบนแต่ว่าส่วนwlสูงแย่ลง -1429 QDSC_InSb_GaSb_sweep_InSb_pn
# srh 1 rad 1 aug 0 sur 0 gen 0  เชี้ยเลย กระแส -19 res 368 ดีขึ้น but 1600 trend up long wl fk must something to decrees EQE
# srh 1 rad 1 aug 0 sur 1 gen 1  เชี้ยเหมือนกัน
# srh 1 rad 1 aug 0 sur 0 gen 1  เชี้ยเหมือนกัน

# srh 0 rad 1 aug 0 sur 0 gen 0  J: -254. Res 15821 แต่ว่าไม่มีอะไรชูทำให้ 668 ตกและติดลบ
#  con fix aug to 1e-27 --> 1e-28 --> 1e-29
# srh 0 rad 1 aug 1 sur 0 gen 0 fix aug 1e-27 cm6 Res: 21 J: -202 wl: 1324 -0.65e-2 and long at 1407 -790
# srh 0 rad 1 aug 1 sur 0 gen 0 fix aug 1e-28 cm6 Res: 21 J: -202 wl: 1324 -0.86e-2 and long at 1407 -791 ดูดีขึ้นตัวนี้
# srh 0 rad 1 aug 1 sur 0 gen 0 fix aug 1e-29 cm6 Res: 21 J: -202 มี +- wl: 1324 -0.29e-1 and long at 1407 -792

#  add AlGaAs and
#        Layer(width=si(f"{100} nm"), material=i_GaAs_barrier, role="interlayer"),
#        Layer(width=si(f"{i} nm"), material=InSb, role="well"),
#        Layer(width=si(f"{100} nm"), material=i_GaAs, role="interlayer"),
#        Layer(width=si(f"{size_GaSb} nm"), material=GaSb, role="well"),  # 5-20 nm
#        Layer(width=si(f"{50} nm"), material=i_GaAs_barrier, role="interlayer"),
#         x5
# srh 0 rad 1 aug 1 sur 0 gen 0 fix aug 1e-29 cm6 Res: 20.8 J: -204
# srh 0 rad 1 aug 1 sur 0 gen 1 fix aug 1e-29 cm6 Res 20.8 J:-204 มีภาพ 1354 -0.18e-3 แต่ว่าส่วนหลังๆ runaway ไปทางลบ
# srh 0 rad 1 aug 1 sur 0 gen 1 Res 20.8 J:-204 มีภาพ 1354 -0.18e-3 แต่ว่าส่วนหลังๆ runaway ไปทางลบ
# srh 1 rad 1 aug 1 sur 0 gen 1 Res 20.8 J:-204 1354 -0.262906E-03 แต่ว่าส่วนหลังๆ runaway แต่ช้าลง
#        Layer(width=si(f"{100} nm"), material=i_GaAs_barrier, role="well"),
#        Layer(width=si(f"{i} nm"), material=InSb, role="well"),
#        Layer(width=si(f"{100} nm"), material=i_GaAs, role="well"),
#        Layer(width=si(f"{size_GaSb} nm"), material=GaSb, role="well"),  # 5-20 nm
#        Layer(width=si(f"{50} nm"), material=i_GaAs_barrier, role="well"),
#         x5
# srh 1 rad 1 aug 1 sur 0 gen 1 เลขบนเป็นบวก J:-204 Res: 20.8  wl 807: -104963.
# srh 0 rad 1 aug 1 sur 0 gen 0 เลขบนเป็นบวก J:-204 Res: 20.8  wl 802: -98277.
# srh 0 rad 1 aug 0 sur 0 gen 0 เลขบนเป็นบวก J:-295 Res: 12441  wl 1129: -0.107322E-02 and runaway minus
# srh 1 rad 1 aug 0 sur 0 gen 0  J:-295 Res: 12441  wl 1354.20: -0.617E-05 and runaway minus
# srh 1 rad 1 aug 1 sur 0 gen 0 เลขบนเป็นบวก J:-204 Res: 20.8  เหมือนเดิม
# srh 1 rad 1 aug 0 sur 0 gen 1 เลขบนเป็นบวก J:-204 Res: 20.8  เหมือนเดิม
# srh 1 rad 1 aug 0 sur 1 gen 1 เลขบนดีขึ้น J:-204 Res: 20.8  wl 1354: -0.616955E-05 and runaway minus ดีขึ้น
#        Layer(width=si(f"{100} nm"), material=i_GaAs_barrier, role="well"),
#        Layer(width=si(f"{i} nm"), material=InSb, role="well"),
#        Layer(width=si(f"{100} nm"), material=i_GaAs, role="well"),
#        Layer(width=si(f"{size_GaSb} nm"), material=GaSb, role="well"),  # 5-20 nm
#        Layer(width=si(f"{50} nm"), material=i_GaAs_barrier, role="well"),
#         x4 --> x6
# srh 1 rad 1 aug 0 sur 1 gen 1 เลขบนเป็นบวก J:-203 Res: 21  wl 1354: -0.232454E-03 and -101656 แย่ลง x4
# srh 1 rad 1 aug 0 sur 1 gen 1 เลขบนเป็นบวก J:-203 Res: 21  wl 1354: -0.508789E-05 and runaway minus ดีขึ้น x6 stack
# srh 1 rad 1 aug 0 sur 1 gen 1 เลขบนปรกติ J:-203 Res: 24  wl 1354: -0.573689E-05 and runaway minus ดีขึ้น x1 stack
# srh 1 rad 1 aug 1 sur 1 gen 1 เลขบนเป็นบวก J:-201 Res: 24  wl 1354: -0.486986E-05 and runaway minus ดีขึ้น x1 stack V สูงขึ้นแล้ว

# srh 1 rad 1 aug 1 sur 1 gen 0 เลขบนเป็นบวก J:-203 Res: 24  wl 1354: -0.486986E-05 and runaway minus ดีขึ้น x1 stack V สูงขึ้นแล้ว
# change AlGaAs to 50 nm and wl 350-1700 nm
# srh 1 rad 1 aug 1 sur 1 gen 0 เลขบนเป็นบวก J:-203 Res: 24  wl 1354: -0.373742E-03 and runaway minus แย่ลง x1 stack V
# change AlGaAs to 100 nm + strained and wl 350-1700 nm
# srh 1 rad 1 aug 1 sur 1 gen 0 เลขบนเป็นบวก J: -201 Res: 24  wl 1354: -0.225507E-02 and -51653 x1 แย่ลง stack
# wl 350-2000 nm
# srh 1 rad 1 aug 1 sur 1 gen 0 เลขบนเป็นบวก J: -201 Res: 24  wl 1354: -0.486986E-05 and runaway x1 แย่ลง stack

# change AlGaAs to 100 nm remove strained and wl 350-1700 nm
# srh 1 rad 1 aug 1 sur 1 gen 0 เลขบนเป็นบวก J: -201 Res: 24  wl 1354: -0.225507E-02 and -51653 x1 แย่ลง stack
# wl 350-2500 nm error --> 350-2000 nm remove AlGaAs
# [
#                 Layer(width=si(f"{100} nm"), material =i_GaAs_barrier, role="well"),
#                 Layer(width=si(f"{i} nm"), material=InSb, role="well"),
#                 Layer(width=si(f"{100} nm"), material=i_GaAs, role="interlayer"),
#                 Layer(width=si(f"{size_GaSb} nm"), material=GaSb, role="well"),  # 5-20 nm
#                 Layer(width=si(f"{50} nm"), material=i_GaAs_barrier, role="well"),
#             ]
# srh 1 rad 1 aug 1 sur 1 gen 0 เลขกระแสปรกติ J: -201 Res: 24  wl 1132: -7.51129  and runaway ลองให้ I ห่างขึ้น (รันเร็วขึ้น)
# add i_GaAs
# srh 1 rad 1 aug 1 sur 1 gen 0 เลขกระแสเป็นบวกลบ J: -201 Res: 22.7  wl 1132: -0.100687E-02 and -7.51129 ลองให้ I ห่างขึ้น
# change to AlGaAs Al=0.4
# srh 1 rad 1 aug 1 sur 1 gen 0 เลขกระแสปรกติ J: -201 Res: 24.2  wl 1354: -0.183705E-04 and runaway
# srh 0 rad 1 aug 1 sur 1 gen 1 เลขบนเป็นบวก J: -201 Res: 24.2  wl 1354: -0.725411E-05 and runaway ลองให้ I ห่างขึ้น
# srh 0 rad 1 aug 1 sur 1 gen 0 เลขบนเป็นบวก J: -201 Res: 24.2  wl 1354: -0.725411E-05 and runaway ลองให้ I ห่างขึ้น
# srh 0 rad 1 aug 0 sur 1 gen 0 เลขบนเป็นบวก J: -201 Res: 24.2  wl 1354.89: -0.151255E-03 and runaway
#  con fix aug to 1e-30 add aug to GaSb
# srh 0 rad 1 aug 1 sur 1 gen 0 เลขบนเป็นบวก J: -201 Res: 24.2  wl 1354.89: -0.151255E-03 and runaway
# add aug to GaSb
# srh 0 rad 1 aug 1 sur 1 gen 0 เลขบนเป็นบวก J: -201 Res: 24.2  wl 1354.89: -0.158803E-04 and -87872
# srh 1 rad 1 aug 1 sur 1 gen 0 เลขบนเป็นบวก J: -201 Res: 24.2  wl 1354.89: -0.177417E-04 and runaway
# srh 1 rad 1 aug 1 sur 1 gen 0 เลขบนเป็นบวก J: -201 Res: 24.2  wl 1354.89: -0.177417E-04 and runaway  V เพิ่ม 0.360360E-1
# srh 0 rad 1 aug 0 sur 1 gen 0 เลขเป็นลบแบบแปลกๆ J: -219 Res: 16677.2  wl 1094.89: -0.151255E-03 and runaway แต่ V เพื่มเป็น 0.5!!!!!!! แค่ตัวแรก ที่เหลือพังหมด
# srh 1 rad 1 aug 1 sur 1 gen 0 เลขบนเป็นบวก J: -201 Res: 24.2  wl 1354.89: -0.177417E-04 and runaway  V เพิ่ม 0.360360E-1 พังเหมือนันหมก

# srh 1 rad 1 aug 1 sur 0 gen 0 เลขบนเป็นบวก ระเบิด
# srh 0 rad 1 aug 1 sur 0 gen 0 เลขบนเป็นบวก อันแรกระเบิด อันสองดีขึ้นแต่ระเบิดอยู้ดี
# fix p length to 400 nm
# srh 0 rad 0 aug 0 sur 1 gen 0 every thing work
# srh 1 rad 1 aug 1 sur 1 gen 1 fail
# srh 0 rad 1 aug 1 sur 1 gen 0 fail
# change lifetime to 1e-6 to InSb
# srh 0 rad 1 aug 0 sur 0 gen 0 fail
# srh 0 rad 0 aug 0 sur 0 gen 0 fail
# change lifetime to 1e-6 to GaSb
# srh 0 rad 0 aug 0 sur 0 gen 0 fail
# srh 0 rad 1 aug 0 sur 0 gen 0 worst
# change lifetime to GaSb to off and 1e-9 to InSb
# srh 0 rad 1 aug 0 sur 0 gen 0 worst
# change hole lifetime 1e-10 to InSb
# srh 0 rad 1 aug 0 sur 0 gen 0 worst
# srh 0 rad 0 aug 0 sur 0 gen 0 get better but fail Res:7484
# change hole lifetime 1e-11 to InSb
# change to np and change n-doped
# srh 0 rad 0 aug 0 sur 0 gen 0 Jมีบวกลบตอนแรก: -197 Res:34 EQE 933: -0.65E-2
# wl 350-3000nm
# srh 0 rad 0 aug 0 sur 0 gen 0 Jมีบวกลบตอนแรก: -197 Res:34 EQE 933: -0.65E-2
# 5x stack
# srh 0 rad 0 aug 0 sur 0 gen 0 J norm: -197 Res:34 EQE 1355: -0.345E-3 and constant !!!!!!! V is work
# srh 0 rad 1 aug 0 sur 0 gen 0 J frist not good: -215 Res: 8159 EQE drop:
# srh 1 rad 0 aug 0 sur 0 gen 0 J frist good: -200 Res: 33 EQE drop:
# srh 0 rad 0 aug 1 sur 0 gen 0 J frist not good: -200 Res: 33 EQE drop:
# srh 0 rad 0 aug 0 sur 0 gen 1 J frist good: -200 Res: 34 EQE 1355 drop: -0.344767E-03
# change hole lifetime 1e-10 electron 1e-6 to InSb
# srh 0 rad 0 aug 0 sur 0 gen 1 J frist good: -200 Res: 34 EQE 1355 drop: -0.344767E-03
# srh 0 rad 1 aug 0 sur 0 gen 1 J frist good: -200 Res: 34 EQE 588 drop: -0.344767E-03
#stack 4
# srh 0 rad 1 aug 0 sur 0 gen 1 J abnorm: -208 Res 7916 EQE 631 drop: -0.344767E-03
#stack 3
# srh 1 rad 1 aug 0 sur 0 gen 1 J abnorm: -215 Res 205 EQE work Voltage 0.2
# srh 1 rad 1 aug 1 sur 0 gen 1 J abnorm: -194 Res 662 EQE don't work
#hole_minority_lifetime InSb 1e-10--> 1e-11
# srh 1 rad 1 aug 1 sur 0 gen 1 J abnorm: -196 Res 546 EQE 952: don't work Voltage 0.2
# srh 1 rad 1 aug 0 sur 0 gen 1 J abnorm: -233 Res 1611115 EQE runaway
#electron_minority_lifetime InSb 1e-6--> 1e-7
# srh 1 rad 1 aug 1 sur 0 gen 1 J almost norm but +-: -199 Res 391 EQE  don't work Voltage 0.2
#hole_minority_lifetime InSb 1e-10--> 1e-9
# srh 1 rad 1 aug 0 sur 0 gen 1 J abnorm: -221 Res 139 EQE runaway
#hole_minority_lifetime InSb 1e-9--> 1e-10
# srh 1 rad 1 aug 0 sur 0 gen 1 J abnorm: -221 Res 205 EQE work Voltage 0.2
#stack x5-->x4
# srh 1 rad 1 aug 0 sur 0 gen 1 J abnorm: -215 Res 205 EQE work Voltage 0.2
#stack x4-->x3
# srh 1 rad 1 aug 0 sur 0 gen 1 J abnorm: -215 Res 205 EQE work Voltage 0.2
# srh 1 rad 1 aug 0 sur 1 gen 1 J abnorm: -215 Res 205 EQE work Voltage 0.2
#stack x3-->x1
# srh 1 rad 1 aug 0 sur 1 gen 1 J abnorm but better: -198 Res 257 EQE work drop and minus Voltage 0.2
#stack x1-->x2
# srh 1 rad 1 aug 0 sur 1 gen 1 J abnorm but better: 502 Res 46017 EQE runaway and minus Voltage 0.2
#                    Layer(width=si("100 nm"), material=n_GaAs_window, role="Emitter"),
#                    Layer(width=si("150 nm"), material=n_GaAs, role="Emitter"),
#                + QW_list
#                    Layer(width=si("150 nm"), material=n_GaAs, role="Emitter"),
#                    Layer(width=si("1800 nm"), material=p_GaAs, role="Base"),
#                    Layer(width=si("100 nm"), material=p_GaInP, role="BSF"),
#                    Layer(width=si("150 nm"), material=p_GaAs_buffer, role="Buffer"),
#electron_minority_lifetime InSb 1e-7 --> 1e-6
# stack x2--> x3
# srh 1 rad 1 aug 0 sur 1 gen 1 J abnorm: -233 Res 519 WL 917: -0.299514E-02
#                 Layer(width=si(f"{50} nm"), material=i_GaAs_barrier, role="well"),
#                 Layer(width=si(f"{i} nm"), material=InSb, role="well"),
#                 Layer(width=si(f"{50} nm"), material=i_GaAs, role="interlayer"),
#                 Layer(width=si(f"{size_GaSb} nm"), material=GaSb, role="well"),  # 5-20 nm
#                 Layer(width=si(f"{50} nm"), material=i_GaAs_barrier, role="well"),
# srh 1 rad 1 aug 0 sur 1 gen 1 J abnorm: -198 Res 64008 WL 1254: -0.168449E-03
#                 Layer(width=si("100 nm"), material=n_GaAs_window, role="Emitter"),
# srh 1 rad 1 aug 0 sur 1 gen 1 J abnorm: -209 Res 10664 WL good(best)
#                 Layer(width=si("150 nm"), material=n_GaAs_window, role="Emitter"),
# srh 1 rad 1 aug 0 sur 1 gen 1 J abnorm: -212 Res 12380 WL good(best) better very good but voltage
# hole_minority_lifetime 1e-10 --> 1e-9 InSb
# srh 1 rad 1 aug 0 sur 1 gen 1 J abnorm: -211 Res 95 WL good(best) better very good but voltage
#                 Layer(width=si(f"{50} nm"), material=i_GaAs_barrier, role="barrier"),
#                 Layer(width=si(f"{i} nm"), material=InSb, role="well"),
#                 Layer(width=si(f"{50} nm"), material=i_GaAs, role="well"),
#                 Layer(width=si(f"{size_GaSb} nm"), material=GaSb, role="well"),  # 5-20 nm
#                 Layer(width=si(f"{50} nm"), material=i_GaAs_barrier, role="barrier"),
# srh 1 rad 1 aug 0 sur 1 gen 1 J abnorm: -199 Res 27 WL good(best) better very good but voltage
# sim at 1 nm
# srh 1 rad 1 aug 0 sur 1 gen 1 J abnorm: +100 Res 27 WL
# Layer(width=si("50 nm"), material=n_GaAs_window, role="Emitter"),
# srh 1 rad 1 aug 0 sur 1 gen 1 J abnorm: -199 Res 179517 WL fail
# add doping at p
# srh 1 rad 1 aug 0 sur 1 gen 1 J abnorm: -199 Res 179517 WL fail
#                  Layer(width=si(f"{50} nm"), material=i_GaAs_barrier, role="barrier"),
#                  Layer(width=si(f"{i} nm"), material=InSb, role="well"),
#                  Layer(width=si(f"{100} nm"), material=i_GaAs, role="barrier"),
#                  Layer(width=si(f"{size_GaSb} nm"), material=GaSb, role="well"),  # 5-20 nm
#                  Layer(width=si(f"{50} nm"), material=i_GaAs_barrier, role="barrier"),
# srh 1 rad 1 aug 0 sur 1 gen 1 J abnorm: -199 Res 21 WL good(best) better very good but voltage
#                                      Layer(width=si("50 nm"), material=n_GaAs_window, role="Emitter"),
#                                      Layer(width=si("150 nm"), material=n_GaAs, role="Emitter"),
#                                      Layer(width=si(f"100 nm"), material=n_AlGaAs, role="barrier"),
#                                  + QW_list
#                                      Layer(width=si(f"100 nm"), material=n_AlGaAs, role="barrier"),
#                                      Layer(width=si("150 nm"), material=n_GaAs, role="Emitter"),
#                                      Layer(width=si("1800 nm"), material=p_GaAs, role="Base"),
#                                      Layer(width=si("100 nm"), material=p_GaInP, role="BSF"),
#                                      Layer(width=si("150 nm"), material=p_GaAs_buffer, role="Buffer"),
# srh 1 rad 1 aug 0 sur 1 gen 1 J abnorm: -201 Res 21 WL fail
#                 Layer(width=si(f"{100} nm"), material=AlGaAs, role="barrier"),
#                 Layer(width=si(f"{i} nm"), material=InSb, role="well"),
#                 Layer(width=si(f"{100} nm"), material=AlGaAs, role="barrier"),
#                 Layer(width=si(f"{size_GaSb} nm"), material=GaSb, role="well"),  # 5-20 nm
#                 Layer(width=si(f"{100} nm"), material=AlGaAs, role="barrier"),
# srh 1 rad 1 aug 0 sur 1 gen 1 J abnorm: -201 Res 21 WL fail but look better
#                 Layer(width=si(f"{25} nm"), material=AlGaAs, role="barrier"),
#                 Layer(width=si(f"{i} nm"), material=InSb, role="well"),
#                 Layer(width=si(f"{15} nm"), material=AlGaAs, role="barrier"),
#                 Layer(width=si(f"{size_GaSb} nm"), material=GaSb, role="well"),  # 5-20 nm
#                 Layer(width=si(f"{25} nm"), material=AlGaAs, role="barrier"),
# srh 1 rad 1 aug 0 sur 1 gen 1 J abnorm: -201 Res 21 WL fail but look better
#                              Layer(width=si("50 nm"), material=n_GaAs_window, role="Emitter"),
#                              Layer(width=si("150 nm"), material=n_GaAs, role="Emitter"),
#                              Layer(width=si(f"100 nm"), material=n_AlGaAs, role="barrier"),
#                          + QW_list
#                              Layer(width=si("1800 nm"), material=p_GaAs, role="Base"),
#                              Layer(width=si("100 nm"), material=p_GaInP, role="BSF"),
#                              Layer(width=si("150 nm"), material=p_GaAs_buffer, role="Buffer"),
# srh 1 rad 1 aug 0 sur 1 gen 1 J norm: -196 Res 27 WL so realistic 1636:-0.139453E-07 don't runaway!!! miraical
#                 Layer(width=si(f"{100} nm"), material=AlGaAs, role="barrier"),
#                 Layer(width=si(f"{i} nm"), material=InSb, role="well"),
#                 Layer(width=si(f"{100} nm"), material=AlGaAs, role="barrier"),
#                 Layer(width=si(f"{size_GaSb} nm"), material=GaSb, role="well"),  # 5-20 nm
#                 Layer(width=si(f"{100} nm"), material=AlGaAs, role="barrier"),
# srh 1 rad 1 aug 0 sur 1 gen 1 J norm: -187 Res 25 WL so realistic 1636:-0.139453E-15 runaway
# lower doped
#                 Layer(width=si(f"{25} nm"), material=AlGaAs, role="barrier"),
#                 Layer(width=si(f"{i} nm"), material=InSb, role="well"),
#                 Layer(width=si(f"{15} nm"), material=AlGaAs, role="barrier"),
#                 Layer(width=si(f"{size_GaSb} nm"), material=GaSb, role="well"),  # 5-20 nm
#                 Layer(width=si(f"{25} nm"), material=AlGaAs, role="barrier"),
# srh 1 rad 1 aug 0 sur 1 gen 1 J norm: -190 Res 3277 WL so realistic 1636:-0.139453E-15 runaway miraical again
# srh 0 rad 1 aug 0 sur 1 gen 1 J abnorm: -190 Res 3277 WL so realistic 1636:-0.139453E-15 runaway miraical again
# disable window and change to n_AlGaAs stack x5
#                   Layer(width=si("100 nm"), material=n_GaAs_window, role="Emitter"),
#                   Layer(width=si("30 nm"), material=n_AlInP, role="window"),
#                   Layer(width=si(f"200 nm"), material=n_AlGaAs, role="barrier"),
#                                  + QW_list
#                   Layer(width=si("1800 nm"), material=p_GaAs, role="Base"),
#                   Layer(width=si("100 nm"), material=p_GaInP, role="BSF"),
#                   Layer(width=si("150 nm"), material=p_GaAs_buffer, role="Buffer"),
# srh 1 rad 1 aug 0 sur 1 gen 1 J abnorm: -196 Res 26 WL so realistic 1636:-0.139453E-15 runaway miraical again
# srh 1 rad 1 aug 1 sur 1 gen 1 J abnorm: -196 Res 26 WL so realistic 1636:-0.139453E-15 runaway miraical again
#wait for runing
# srh 1 rad 1 aug 1 sur 0 gen 0 J abnorm: -196 Res 26 WL so realistic 1636:-0.139453E-15 runaway miraical again
#wait for runing
# srh 0 rad 0 aug 0 sur 0 gen 0 J abnorm: -196 Res 26 WL so realistic 1636:-0.139453E-15 runaway miraical again
# ติดลบจะไม่ออก
#radiative_recombination InSb --> 5e-12 GaSb --> 5e-11
# srh 0 rad 1 aug 1 sur 1 gen 0 Voltage is bad  0.470470  -339.085
#electron_auger_recombination InSb --> 1e-31 and radiative_recombination --> 1e-15 electron_lifetime --> 1e-6
#electron_auger_recombination GaSb --> 1e-31 and radiative_recombination --> 1e-15 electron_lifetime --> 1e-6
# srh 1 rad 1 aug 0 sur 0 gen 0 Voltage is bad  0.470470  -339.085
#electron_auger_recombination InSb --> 1e-31 and radiative_recombination --> 5e-11 electron_lifetime --> 1e-7
#electron_auger_recombination GaSb --> 1e-31 and radiative_recombination --> off electron_lifetime --> 1e-7
# srh 1 rad 1 aug 0 sur 0 gen 0 Voltage is bad  0.470470  -339.085
#electron_auger_recombination InSb --> 1e-31 and radiative_recombination --> 5e-11 electron_lifetime --> 1e-8
# srh 1 rad 1 aug 0 sur 0 gen 0 got lower current but still minus
#electron_auger_recombination InSb --> 1e-31 and radiative_recombination --> 5e-11 electron_lifetime --> 1e-6
# srh 1 rad 1 aug 0 sur 0 gen 0 got lower current but still minus but look better
#electron_auger_recombination InSb --> 1e-31 and radiative_recombination --> 5e-11 hole_lifetime --> 1e-8
# srh 1 rad 1 aug 0 sur 0 gen 0 got lower current but still minus but look better
#electron_auger_recombination InSb --> 1e-31 and radiative_recombination --> 5e-11 hole_lifetime --> 1e-10
# srh 1 rad 1 aug 0 sur 0 gen 0 got lower current but still minus don't change
#electron_auger_recombination InSb --> 1e-31 and radiative_recombination --> 5e-12 hole_lifetime --> 1e-10

flash = State()

flash.meshpoints = 3000
flash.growth_rate = 0.5
flash.coarse = 20e-9
flash.fine = 1e-9
flash.ultrafine = 0.2e-9

flash.clamp = 10
flash.nitermax = 1000
flash.ATol = 1.5e-9
flash.RTol = 1e-4

flash.srh = 0
flash.rad = 0
flash.aug = 0
flash.sur = 0
flash.gen = 0



# to insert AlGaAs in structure by get AlGaAs out side of dot
if __name__ == '__main__':
    # version = "solar_cell_InSb_and_GaSb_like_paper"
    # set_of_data_sun_constant = load_old_data('solar_cell_InSb_and_GaSb_like_paper.pkl')
    # # for i in set_of_data_sun_constant:
    # #     print(i)
    # # print(len(set_of_data_sun_constant))
    # # print(len(set_of_data_sun_constant))
    #
    # save_set_of_data_sun_constant(set_of_data_sun_constant, version, focus_area=(300, 3500))
    # try:
    #     movefile(f'Carrier_distribution_{version}.html', f'{version}')
    #     movefile(f'Carrier_distribution_{version}_zoom.html', f'{version}')
    #     movefile(f'Band_diagramming_of_{version}.html', f'{version}')
    #     movefile(f'Band_diagramming_of_{version}_zoom.html', f'{version}')
    # except PermissionError as e:
    #     print(f"Error: {e}")
    # plt.show()
    version = "QDSC_InSb_GaSb_sweep_InSb_pn_ver_3"
    sim_mat, plot_note = QDSC_InSb_GaSb_sweep_InSb_pn()
    note = f"""
       T=300
       vint = np.linspace(-3, 3, 1000)
       wl = np.linspace(350, 2500, 1000) *1e-9   # version1
       V = np.linspace(-1.5, 0, 500)  # np
       recalculate_absorption = False
       meshpoints ={normal_operation.meshpoints}
       growth_rate = {normal_operation.growth_rate}
       coarse = {normal_operation.coarse}
       fine = {normal_operation.fine}
       ultrafine = {normal_operation.ultrafine}

       clamp = {normal_operation.clamp}
       nitermax = {normal_operation.nitermax}
       ATol = {normal_operation.ATol}
       RTol = {normal_operation.RTol}

       srh = {normal_operation.srh}
       rad = {normal_operation.rad}
       aug = {normal_operation.aug}
       sur = {normal_operation.sur}
       gen = {normal_operation.gen}

       recalculate_absorption = {normal_operation.recalculate_absorption}
       radiative_coupling: False
       optics_method: "TMM",
       """
    sim1D_sun_constant(version, sim_mat, plot_note, note, pdd_options=normal_operation)

    # #
    # version = "QDSC_InSb_GaSb_sweep_InSb_AlGaAs_n_type_report"
    # sim_mat, plot_note = QDSC_InSb_GaSb_sweep_InSb_AlGaAs_n_type()
    # note = f"""
    # T=300
    # vint = np.linspace(-3, 3, 1000)
    # wl = np.linspace(350, 3000, 1000) *1e-9   # version1
    # V = np.linspace(-1.5, 1.5, 1000)  # np
    # recalculate_absorption = False
    # meshpoints ={normal_operation.meshpoints}
    # growth_rate = {normal_operation.growth_rate}
    # coarse = {normal_operation.coarse}
    # fine = {normal_operation.fine}
    # ultrafine = {normal_operation.ultrafine}
    #
    # clamp = {normal_operation.clamp}
    # nitermax = {normal_operation.nitermax}
    # ATol = {normal_operation.ATol}
    # RTol = {normal_operation.RTol}
    #
    # srh = {normal_operation.srh}
    # rad = {normal_operation.rad}
    # aug = {normal_operation.aug}
    # sur = {normal_operation.sur}
    # gen = {normal_operation.gen}
    #
    # recalculate_absorption = {normal_operation.recalculate_absorption}
    # radiative_coupling: False
    # optics_method: "TMM",
    # """
    # sim1D_sun_constant(version, sim_mat, plot_note, note, pdd_options=normal_operation)

    # normal_operation3 = State()
    #
    # normal_operation3.meshpoints = -400
    # normal_operation3.growth_rate = 0.5
    # normal_operation3.coarse = 20e-9
    # normal_operation3.fine = 1e-9
    # normal_operation3.ultrafine = 0.2e-9
    #
    # normal_operation3.clamp = 10
    # normal_operation3.nitermax = 1000
    # normal_operation3.ATol = 1.5e-09
    # normal_operation3.RTol = 1e-4
    #
    # normal_operation3.srh = 0
    # normal_operation3.rad = 1
    # normal_operation3.aug = 0
    # normal_operation3.sur = 0
    # normal_operation3.gen = 0
    # version = "QDSC_InSb_GaSb_sweep_InSb_pn_rad"
    # sim_mat, plot_note = QDSC_InSb_GaSb_sweep_InSb_pn()
    # note = f"""
    #    T=300
    #    vint = np.linspace(-6, 4, 1000)
    #    V = np.linspace(-1.5, 0, 500)  # np
    #    wl = np.linspace(350, 1200, 500) *1e-9   # version1
    #    recalculate_absorption = False
    #    meshpoints ={normal_operation3.meshpoints}
    #    growth_rate = {normal_operation3.growth_rate}
    #    coarse = {normal_operation3.coarse}
    #    fine = {normal_operation3.fine}
    #    ultrafine = {normal_operation3.ultrafine}
    #
    #    clamp = {normal_operation3.clamp}
    #    nitermax = {normal_operation3.nitermax}
    #    ATol = {normal_operation3.ATol}
    #    RTol = {normal_operation3.RTol}
    #
    #    srh = {normal_operation3.srh}
    #    rad = {normal_operation3.rad}
    #    aug = {normal_operation3.aug}
    #    sur = {normal_operation3.sur}
    #    gen = {normal_operation3.gen}
    #    radiative_coupling: False
    #    optics_method: "TMM",
    #    """
    # sim1D_sun_constant(version, sim_mat, plot_note, note, pdd_options=normal_operation3)
    # version = "dot_InSb_n_bot_sweep"
    # sim_mat, plot_note = dot_InSb_n_bot_sweep()
    # note = f"""
    #    T=300
    #    vint = np.linspace(-6, 4, 1000)
    #    V = np.linspace(-1.5, 0, 500)  # np
    #    wl = np.linspace(350, 1200, 500) *1e-9   # version1
    #    recalculate_absorption = False
    #    meshpoints ={normal_operation.meshpoints}
    #    growth_rate = {normal_operation.growth_rate}
    #    coarse = {normal_operation.coarse}
    #    fine = {normal_operation.fine}
    #    ultrafine = {normal_operation.ultrafine}
    #
    #    clamp = {normal_operation.clamp}
    #    nitermax = {normal_operation.nitermax}
    #    ATol = {normal_operation.ATol}
    #    RTol = {normal_operation.RTol}
    #
    #    srh = {normal_operation.srh}
    #    rad = {normal_operation.rad}
    #    aug = {normal_operation.aug}
    #    sur = {normal_operation.sur}
    #    gen = {normal_operation.gen}
    #    radiative_coupling: False
    #    optics_method: "TMM",
    #    """
    # sim1D_sun_constant(version, sim_mat, plot_note, note, pdd_options=normal_operation)
    # version = "QDSC_InSb_GaSb_sweep_InSb_pn_try"
    # set_of_data_sun_constant = load_old_data('QDSC_InSb_GaSb_sweep_InSb_pn_try.pkl')
    # # for i in set_of_data_sun_constant:
    # #     print(i)
    # # print(len(set_of_data_sun_constant))
    # # print(len(set_of_data_sun_constant))
    #
    # save_set_of_data_sun_constant(set_of_data_sun_constant, version, focus_area=(300, 3500))
    # try:
    #     movefile(f'Carrier_distribution_{version}.html', f'{version}')
    #     movefile(f'Carrier_distribution_{version}_zoom.html', f'{version}')
    #     movefile(f'Band_diagramming_of_{version}.html', f'{version}')
    #     movefile(f'Band_diagramming_of_{version}_zoom.html', f'{version}')
    # except PermissionError as e:
    #     print(f"Error: {e}")
    plt.show()