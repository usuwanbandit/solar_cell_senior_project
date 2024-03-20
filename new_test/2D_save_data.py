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
    y_axis=[],
    y_axis_name='None',
    mode_x='None',
    mode_y="None",
)


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


def save_2D_set_of_data_sun_constant(all_data, version, focus_area=None):
    if focus_area is None:
        focus_area = (100, 650)
    simpifly = None
    lenx = len(all_data)
    leny = len(all_data[0])
    fig, ax1 = plt.subplots(1, 1, figsize=(6, 4))
    fig_5, ax1_5 = plt.subplots(1, 1, figsize=(6, 4))
    fig1, axes = plt.subplots(2, 2, figsize=(11.25, 8))
    fig2, axIV = plt.subplots(1, 1, figsize=(8, 6))
    fig3, axCar = plt.subplots(lenx, leny, figsize=(16, 5 * lenx * leny))
    fig3_5, axCar2 = plt.subplots(lenx, leny, figsize=(16, 5 * lenx * leny))
    fig_b1, band1 = plt.subplots(lenx, leny, figsize=(16, 5 * lenx * leny))
    fig_b2, band2 = plt.subplots(lenx, leny, figsize=(16, 5 * lenx * leny))
    if lenx > 5:
        simpifly = np.linspace(0, lenx, 5)
        simpifly = [int(i) for i in simpifly].append(lenx - 1)
    Pmpp = []
    Isc = []
    Voc = []
    FF = []
    for set_of_data in all_data:
        Pmpp_x = []
        Isc_x = []
        Voc_x = []
        FF_x = []
        for num, data in enumerate(set_of_data):
            print(f'loading {data["mode"]}')
            ax1.plot(data['qe']["WL"] * 1e9, data["qe"]["EQE"], label=f"{data['mode']} ")
            ax1.legend(loc="upper right", frameon=False)
            ax1.set_xlabel("Wavelength (nm)")
            ax1.set_ylabel("EQE")
            ax1.set_ylim(0, 1.1)
            ax1.set_xlim(350, 1000)
            ax1.legend()
            plt.tight_layout()
            fig1.suptitle(f"{version}")

            ax1_5.semilogy(data['qe']["WL"] * 1e9, data["qe"]["EQE"], label=f"{data['mode']} ")
            ax1_5.legend(loc="upper right", frameon=False)
            ax1_5.set_xlabel("Wavelength (nm)")
            ax1_5.set_ylabel("EQE")
            ax1_5.set_ylim(1e-8, 1)
            ax1_5.set_xlim(900, 1200)
            ax1_5.legend()
            fig_5.suptitle(f"{version}")

            linestyle = ["-", "--", ":", "-.", ]
            # marker = [".", ",", "o", 'v', "^", "<", ">", "s", "p", "*", "h", "+", "x", "D", "d"]
            color = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black', 'orange', 'purple']
            Pmpp_x.append(data["iv"]["Pmpp"])
            Isc_x.append(data["iv"]["Isc"])
            Voc_x.append(data["iv"]["Voc"])
            FF_x.append(data["iv"]["FF"])

            axIV.plot(-data["iv"]["IV"][0], data["iv"]["IV"][1] / -10, label=f"{data['mode']}")
            axIV.set_ylim(0, 30)
            axIV.set_xlim(-0.1, 1.5)
            axIV.set_xlabel("Voltage (V)")
            axIV.set_ylabel("J$_{SC}$ (mA/cm$^{2}$)")
            axIV.legend()
            plt.tight_layout()

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

                plt.tight_layout()

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
                band1[num].plot(x * 1e9, Efc, 'b--', label="Efe")
                band1[num].plot(x * 1e9, Efh, 'r--', label="Efh")
                band1[num].plot(x * 1e9, potential, label="potential")
                band1[num].set_xlabel('Position (nm)')
                band1[num].set_ylabel('Energy (eV)')
                band1[num].legend()

                band2[num].set_title(data["mode"])
                band2[num].plot(x * 1e9, Ec, 'b', label="Ec")
                band2[num].plot(x * 1e9, Ev, 'r', label="Ev")
                band2[num].plot(x * 1e9, Efc, 'b--', label="Efe")
                band2[num].plot(x * 1e9, Efh, 'r--', label="Efh")
                band2[num].plot(x * 1e9, potential, label="potential")
                band2[num].set_xlabel('Position (nm)')
                band2[num].set_ylabel('Energy (eV)')
                band2[num].legend()
                band2[num].set_xlim(focus_area)

            except Exception as error:
                print(f'error is {error}')
        Pmpp.append(Pmpp_x)
        Isc.append(Isc_x)
        Voc.append(Voc_x)
        FF.append(FF_x)

    Pmpp = np.array(Pmpp)
    Isc = np.array(Isc)
    Voc = np.array(Voc)
    FF = np.array(FF)
    # color = [plt.cm.hsv(i / len(set_of_data)) for i in range(len(set_of_data))]
    # axes.text(0.95, 0.95, 'Sample Text', ha='right', va='top', transform=plt.gca().transAxes, fontsize=12)
    # print(Pmpp)
    X, Y = np.meshgrid(all_data[0][0]['x_axis'],all_data[0][0]['y_axis'])
    cs1 = axes[0, 0].contourf(X, Y, Pmpp, 100, cmap=cm.jet)
    axes[0, 0].set_xlabel(all_data[0][0]['x_axis_name'])
    axes[0, 0].set_ylabel(all_data[0][0]['y_axis_name'])
    # axes[0, 0].set_yscale("log")
    # axes[0, 0].set_xscale("log")
    axes[0, 0].set_title("Efficiency (%)")

    cbar1 = fig2.colorbar(cs1)

    cs2 = axes[0, 1].contourf(X, Y, abs(Isc)/10, 100, cmap=cm.jet)
    axes[0, 1].set_xlabel(all_data[0][0]['x_axis_name'])
    axes[0, 1].set_ylabel(all_data[0][0]['y_axis_name'])
    # axes[0, 1].set_yscale("log")
    # axes[0, 1].set_xscale("log")
    axes[0, 1].set_title("Short cir I$_{SC}$ (Am$^{-2}$)")
    cbar2 = fig2.colorbar(cs2)

    cs3 = axes[1, 0].contourf(X, Y, abs(Voc), 100, cmap=cm.jet)
    axes[1, 0].set_xlabel(all_data[0][0]['x_axis_name'])
    axes[1, 0].set_ylabel(all_data[0][0]['y_axis_name'])
    # axes[1, 0].set_yscale("log")
    # axes[1, 0].set_xscale("log")
    axes[1, 0].set_title("Open circuit voltage(V)")
    cbar3 = fig2.colorbar(cs3)

    cs4 = axes[1, 1].contourf(X, Y, abs(FF) * 100, 100, cmap=cm.jet)
    axes[1, 1].set_xlabel(all_data[0][0]['x_axis_name'])
    axes[1, 1].set_ylabel(all_data[0][0]['y_axis_name'])
    # axes[1, 1].set_yscale("log")
    # axes[1, 1].set_xscale("log")
    axes[1, 1].set_title("Fill factor")
    cbar4 = fig2.colorbar(cs4)



    fig.suptitle(f"EQE of  {version}")
    fig_5.suptitle(f"Zoom EQE of {version}")
    fig2.suptitle(f'IV of {version}')
    fig3.suptitle(f"Carrier distribution of {version}")
    fig3_5.suptitle(f"Zoom Carrier distribution of {version}")
    fig_b1.suptitle(f"band gap of {version}")
    fig_b2.suptitle(f"Zoom band gap of {version}")

    plt.tight_layout()
    fig1.tight_layout()
    fig_5.tight_layout()
    fig2.tight_layout()
    fig3.tight_layout()
    fig3_5.tight_layout()
    fig_b1.tight_layout()
    fig_b2.tight_layout()
    # fig1.legend()
    # plt.legend()

    fig.savefig(f'EQE_{version}.png', dpi=300)
    fig_5.savefig(f'EQE_{version}_zoom.png', dpi=300)
    fig1.savefig(f'performance_{version}.png', dpi=300)
    fig2.savefig(f'IV_curve_{version}.png', dpi=300)
    mpld3.save_html(fig3, f'Carrier_distribution_{version}.html')
    mpld3.save_html(fig3_5, f'Carrier_distribution_{version}_zoom.html')
    mpld3.save_html(fig_b1, f'Band_diagramming_of_{version}.html')
    mpld3.save_html(fig_b2, f'Band_diagramming_of_{version}_zoom.html')

    save_file_direction(f'{version}', f'{version}', saveing_data=all_data)

    movefile(f'IV_curve_{version}.png', f'{version}')
    movefile(f'current_curve_{version}.png', f'{version}')
    movefile(f'performance_{version}.png', f'{version}')
    movefile(f'EQE_{version}_zoom.png', f'{version}')
    movefile(f'EQE_{version}.png', f'{version}')
    # movefile(f'carrier_distribution{version}.html', f'{version}')

    # movefile
    print('save complete')


def simulation1D_sun_constant(version, sim_mat, plot_note, pdd_options=None, note='', ):
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
    set_of_data_2D = []
    for mode_y, cell_y in sim_mat.items():
        for mode_x, cell_x in cell_y:
            data_mode = data_solar_cell.copy()
            data_mode['mode_x'] = mode_x
            data_mode['mode_y'] = mode_y
            data_mode['note'] = note
            data_mode['x_axis'] = plot_note['x_axis']
            data_mode['x_axis_name'] = plot_note["x_axis_name"]
            data_mode['y_axis'] = plot_note['y_axis']
            data_mode['y_axis_name'] = plot_note["y_axis_name"]
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
        set_of_data_2D.append(set_of_data)
    return set_of_data_2D



def savecell(cell, pdd_options):
    offset = 0
    pdd_options.position = []
    for junction in cell:
        for layer in junction:
                    if layer.role is not None:
                        pdd_options.position.append(max(1e-10, layer.width / 5000))
                    else:
                        pdd_options.position.append(1e-11)
                    offset += layer.width
    print(pdd_options.position)
    print(len(pdd_options.position))
    solar_cell_solver(cell, "qe",
                      user_options={"light_source": light_source,
                                    "wavelength": wl,
                                    "optics_method": "TMM",
                                    # "internal_voltages": vint,
                                    # "radiative_coupling": True,
                                    # 'recalculate_absorption': pdd_options.recalculate_absorption,
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

def sim1D_sun_constant(version, sim_mat, plot_note, note, pdd_options=None):  # sc = simulation at 1 sun
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
                                                         pdd_options=pdd_options)
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