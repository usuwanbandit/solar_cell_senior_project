import mpld3
import numpy as np
from matplotlib import pyplot as plt, cm, ticker
from numpy import trapz
from simulation_SC import V, wl
from solcore.light_source import LightSource
from lib_save_file import *
# def get_ligth_power(con=None, source_type="standard", version="AM1.5g", ):
#     power_con = None
#     if isinstance(con, list) or isinstance(con, np.ndarray):
#         buffer = []
#         for i in con:
#             light_source_measure = LightSource(
#                 source_type=source_type,
#                 version=version,
#                 output_units='power_density_per_m',
#                 x=wl,
#                 concentration=i, )
#             spectrum = light_source_measure.spectrum()
#             power_buffer = trapz(spectrum, wl)  #
#             buffer.append(power_buffer[1])
#         power_con = np.array(buffer)
#     elif isinstance(con, int):
#         light_source_measure = LightSource(
#             source_type=source_type,
#             version=version,
#             output_units='power_density_per_m',
#             x=wl,
#             concentration=con, )
#         spectrum = light_source_measure.spectrum()
#         power_con = trapz(spectrum, wl)[1]  #
#     return power_con  # W/m2

def defultsave(solarcell, saveaddrest, version, save=True):
    IV_saving = ["Isc", "Voc", "FF", "Pmpp"]
    for i in IV_saving:
        saveaddrest[f"{i}"].append(solarcell.iv[f"{i}"])
    saveaddrest["allI"].append(solarcell.iv["IV"][1])

    if save:
        with open(f'{version}.pkl', 'wb') as fin:
            pickle.dump(saveaddrest, fin)
            print('dictionary saved successfully to file')
    return saveaddrest


def save_ligth(solarcell, saveaddrest, version, save=True):
    saveaddrest["absorbed"].append(solarcell.absorbed)
    for j in solarcell.junction_indices:  # junctionคือหยั่ง
        saveaddrest["xsc"].append(solarcell[j].short_circuit_data.Bandstructure["x"] + solarcell[j].offset)
        saveaddrest["nsc"].append(solarcell[j].short_circuit_data.Bandstructure["n"])
        saveaddrest["psc"].append(solarcell[j].short_circuit_data.Bandstructure["p"])

        saveaddrest["xeq"].append(solarcell[j].equilibrium_data.Bandstructure["x"] + solarcell[j].offset)
        saveaddrest["neq"].append(solarcell[j].equilibrium_data.Bandstructure["n"])
        saveaddrest["peq"].append(solarcell[j].equilibrium_data.Bandstructure["p"])

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

def save_all_file_0d(data, version, con):
    fig, ax1 = plt.subplots(1, 1, figsize=(6, 4))
    fig3, axCar = plt.subplots(1, 1, figsize=(16, 5))

    ax1.plot(wl * 1e9, data["absorbed"][0], label=f"Total Absorbed")
    ax1.legend(loc="upper right", frameon=False)
    ax1.set_xlabel("Wavelength (nm)")
    ax1.set_ylabel("EQE")
    ax1.set_ylim(0, 1.1)
    ax1.set_xlim(350, 1200)
    plt.legend()
    plt.tight_layout()

    fig1, axes = plt.subplots(2, 2, figsize=(11.25, 8))

    axes[0, 0].semilogx(con, np.array(data["Pmpp"]/con/10 ) , "r-o")
    axes[0, 0].set_xlabel("Concentration (suns)")
    axes[0, 0].set_ylabel("Efficiency (%)")

    axes[0, 1].loglog(con, abs(np.array(data["Isc"])), "b-o")
    axes[0, 1].set_xlabel("Concentration (suns)")
    axes[0, 1].set_ylabel("I$_{SC}$ (Am$^{-2}$)")

    axes[1, 0].semilogx(con, abs(np.array(data["Voc"])), "g-o")
    axes[1, 0].set_xlabel("Concentration (suns)")
    axes[1, 0].set_ylabel("V$_{OC}$ (V)")

    axes[1, 1].semilogx(con, abs(np.array(data["FF"])) * 100, "k-o")
    axes[1, 1].set_xlabel("Concentration (suns)")
    axes[1, 1].set_ylabel("Fill Factor (%)")
    fig1.suptitle(f"{version}")
    plt.legend()
    plt.tight_layout()

    fig2, axIV = plt.subplots(1, 1, figsize=(6, 4))
    count = 0
    for i in data["allI"]:
        axIV.plot(-V, i / data["Isc"][count], label=f"x = Concentration (suns) = {con[count]}")
        count += 1

    axIV.set_ylim(0, 1.5)
    axIV.set_xlim(0, 1.5)
    axIV.set_xlabel("Voltage (V)")
    axIV.set_ylabel("I$_{normalize}$ ")
    plt.legend()
    plt.tight_layout()

    try:
        axCar.semilogy(data["xsc"][0] * 1e9, data["nsc"][0], 'b')
        axCar.semilogy(data["xsc"][0] * 1e9, data["psc"][0], 'r')
        axCar.semilogy(data["xeq"][0] * 1e9, data["neq"][0], 'b--')
        axCar.semilogy(data["xeq"][0] * 1e9, data["peq"][0], 'r--')
        plt.legend()
        plt.tight_layout()
    except:
        pass

    fig2.savefig(f'IV_curve_{version}.png', dpi=300)
    fig1.savefig(f'performance_{version}.png', dpi=300)
    fig.savefig(f'EQE_{version}.png', dpi=300)
    mpld3.save_html(fig3, f'Carrier_distribution_{version}.html')

    save_file_direction(f'{version}', f'{version}', saveing_data=[data])



    current_path = os.getcwd()
    movefile(f'IV_curve_{version}.png', f'{version}')
    movefile(f'performance_{version}.png', f'{version}')
    movefile(f'EQE_{version}.png', f'{version}')
    print('save complete')

def save_set_of_data(set_of_data, version, con):
    fig, ax1 = plt.subplots(1, 1, figsize=(6, 4))
    fig1, axes = plt.subplots(2, 2, figsize=(11.25, 8))
    fig2, axIV = plt.subplots(1, 1, figsize=(8, 6))
    fig3, axCar = plt.subplots(len(set_of_data), 1, figsize=(16, 5 * len(set_of_data)))

    for num, data in enumerate(set_of_data):
        print(f'loading {data["mode"]}')
        ax1.plot(wl * 1e9, data["absorbed"][0], label=f"Total Absorbed mode = {data['mode']} ")
        ax1.legend(loc="upper right", frameon=False)
        ax1.set_xlabel("Wavelength (nm)")
        ax1.set_ylabel("EQE")
        ax1.set_ylim(0, 1.1)
        ax1.set_xlim(350, 1200)
        plt.tight_layout()

        # linestyle = ["-", "--", ":", "-."]
        # marker = [".", ",", "o", 'v', "^", "<", ">", "s", "p", "*", "h", "+", "x", "D", "d"]
        # color = ['blue','green','red','cyan','magenta','yellow','black','orange','purple']
        color = [plt.cm.hsv(i / len(set_of_data)) for i in range(len(set_of_data))]

        axes[0, 0].semilogx(con, np.array(data["Pmpp"]) / con / 10, color=color[num], label=f"{data['mode']}")
        axes[0, 0].set_xlabel("Concentration (suns)")
        axes[0, 0].set_ylabel("Efficiency (%)")

        axes[0, 1].loglog(con, abs(np.array(data["Isc"])), color=color[num])
        axes[0, 1].set_xlabel("Concentration (suns)")
        axes[0, 1].set_ylabel("I$_{SC}$ (Am$^{-2}$)")

        axes[1, 0].semilogx(con, abs(np.array(data["Voc"])), color=color[num])
        axes[1, 0].set_xlabel("Concentration (suns)")
        axes[1, 0].set_ylabel("V$_{OC}$ (V)")

        axes[1, 1].semilogx(con, abs(np.array(data["FF"])) * 100, color=color[num])
        axes[1, 1].set_xlabel("Concentration (suns)")
        axes[1, 1].set_ylabel("Fill Factor (%)")

        fig1.suptitle(f"{version}")
        plt.tight_layout()
        fig1.legend()

        for count, i in enumerate(data["allI"]):
            axIV.plot(-V, i / data["Isc"][count],
                      label=f"x = Concentration (suns) = {con[count]} mode = {data['mode']}")

        axIV.set_ylim(0, 1.5)
        axIV.set_xlim(0, 1.5)
        axIV.set_xlabel("Voltage (V)")
        axIV.set_ylabel("I$_{normalize}$ ")
        plt.tight_layout()
        plt.legend()
        try:

            axCar[num].set_title(data["mode"])
            axCar[num].semilogy(data["xsc"][0] * 1e9, data["nsc"][0], 'b')
            axCar[num].semilogy(data["xsc"][0] * 1e9, data["psc"][0], 'r')
            axCar[num].semilogy(data["xeq"][0] * 1e9, data["neq"][0], 'b--')
            axCar[num].semilogy(data["xeq"][0] * 1e9, data["peq"][0], 'r--')
            plt.tight_layout()
            plt.legend()
        except:
            print("something wrong with carrier distibution")
            pass

    plt.legend()
    fig.savefig(f'EQE_{version}.png', dpi=300)
    fig1.savefig(f'performance_{version}.png', dpi=300)
    fig2.savefig(f'IV_curve_{version}.png', dpi=300)
    mpld3.save_html(fig3, f'Carrier_distribution_{version}.html')

    save_file_direction(f'{version}', f'{version}', saveing_data=set_of_data)

    movefile(f'IV_curve_{version}.png', f'{version}')
    movefile(f'performance_{version}.png', f'{version}')
    movefile(f'EQE_{version}.png', f'{version}')
    # movefile(f'carrier_distribution{version}.html', f'{version}')

    # movefile
    print('save complete')


def save_set_of_data_sun_constant(set_of_data, version):
    fig, ax1 = plt.subplots(1, 1, figsize=(6, 4))
    fig1, axes = plt.subplots(2, 2, figsize=(11.25, 8))
    fig2, axIV = plt.subplots(1, 1, figsize=(8, 6))
    fig3, axCar = plt.subplots(len(set_of_data), 1, figsize=(16, 5 * len(set_of_data)))
    Pmpp = []; Isc=[]; Voc=[];FF=[]
    for num, data in enumerate(set_of_data):
        print(f'loading {data["mode"]}')
        ax1.plot(wl * 1e9, data["absorbed"][0], label=f"Total Absorbed mode = {data['mode']} ")
        ax1.legend(loc="upper right", frameon=False)
        ax1.set_xlabel("Wavelength (nm)")
        ax1.set_ylabel("EQE")
        ax1.set_ylim(0, 1.1)
        ax1.set_xlim(350, 1200)
        ax1.legend()

        plt.tight_layout()

        # linestyle = ["-", "--", ":", "-."]
        # marker = [".", ",", "o", 'v', "^", "<", ">", "s", "p", "*", "h", "+", "x", "D", "d"]
        # color = ['blue','green','red','cyan','magenta','yellow','black','orange','purple']
        Pmpp.append(data["Pmpp"])
        Isc.append(data["Isc"])
        Voc.append(data["Voc"])
        FF.append(data["FF"])

        for count, i in enumerate(data["allI"]):
            axIV.plot(-V, i / -10, label=f"mode = {data['mode']}")

        axIV.set_ylim(0, 30)
        axIV.set_xlim(0, 1.5)
        axIV.set_xlabel("Voltage (V)")
        axIV.set_ylabel("J$_{SC}$ (mA/cm$^{2}$)")
        axIV.legend()
        plt.tight_layout()
        try:

            axCar[num].set_title(data["mode"])
            axCar[num].semilogy(data["xsc"][0] * 1e9, data["nsc"][0], 'b')
            axCar[num].semilogy(data["xsc"][0] * 1e9, data["psc"][0], 'r')
            axCar[num].semilogy(data["xeq"][0] * 1e9, data["neq"][0], 'b--')
            axCar[num].semilogy(data["xeq"][0] * 1e9, data["peq"][0], 'r--')
            plt.tight_layout()
            # axCar.legend()
        except:
            print("something wrong with carrier distibution")
            pass
    # color = [plt.cm.hsv(i / len(set_of_data)) for i in range(len(set_of_data))]
    # axes.text(0.95, 0.95, 'Sample Text', ha='right', va='top', transform=plt.gca().transAxes, fontsize=12)
    axes[0, 0].plot(set_of_data[0]['x_axis'], np.array(Pmpp) / 10,color='r')
    axes[0, 0].set_xlabel(set_of_data[0]['x_axis_name'])
    axes[0, 0].set_ylabel("Efficiency (%)")

    axes[0, 1].semilogy(set_of_data[0]['x_axis'], abs(np.array(Isc)),color='g')
    axes[0, 1].set_xlabel(set_of_data[0]['x_axis_name'])
    axes[0, 1].set_ylabel("I$_{SC}$ (Am$^{-2}$)")

    axes[1, 0].plot(set_of_data[0]['x_axis'], abs(np.array(Voc)), color='b')
    axes[1, 0].set_xlabel(set_of_data[0]['x_axis_name'])
    axes[1, 0].set_ylabel("V$_{OC}$ (V)")

    axes[1, 1].plot(set_of_data[0]['x_axis'], abs(np.array(FF))* 100, color='k')
    axes[1, 1].set_xlabel(set_of_data[0]['x_axis_name'])
    axes[1, 1].set_ylabel("Fill Factor (%)")

    fig1.suptitle(f"{version}")
    # plt.tight_layout()
    # fig1.legend()
    # plt.legend()
    fig.savefig(f'EQE_{version}.png', dpi=300)
    fig1.savefig(f'performance_{version}.png', dpi=300)
    fig2.savefig(f'IV_curve_{version}.png', dpi=300)
    mpld3.save_html(fig3, f'Carrier_distribution_{version}.html')

    save_file_direction(f'{version}', f'{version}', saveing_data=set_of_data)

    movefile(f'IV_curve_{version}.png', f'{version}')
    movefile(f'performance_{version}.png', f'{version}')
    movefile(f'EQE_{version}.png', f'{version}')
    # movefile(f'carrier_distribution{version}.html', f'{version}')

    # movefile
    print('save complete')


def save_set_of_data_sun_constant_2D(all_data, version):
    Pmpp = []
    Isc = []
    Voc = []
    FF = []
    for data_y in all_data:
        Pmpp_x = [];
        Isc_x = [];
        Voc_x = [];
        FF_x = []
        for data in data_y:
            print(f'loading {data["mode_x"]}{data["mode y"]}')

            # linestyle = ["-", "--", ":", "-."]
            # marker = [".", ",", "o", 'v', "^", "<", ">", "s", "p", "*", "h", "+", "x", "D", "d"]
            # color = ['blue','green','red','cyan','magenta','yellow','black','orange','purple']
            Pmpp_x.append(data["Pmpp"])
            Isc_x.append(data["Isc"])
            Voc_x.append(data["Voc"])
            FF_x.append(data["FF"])
        Pmpp.append(Pmpp_x)
        Isc.append(Isc_x)
        Voc.append(Voc_x)
        FF.append(FF_x)

    X, Y = np.meshgrid(all_data[0]['x_axis'], all_data[0]['y_axis'])

    # eff = ma.masked_where(eff <= 0, eff)
    fig2, axes = plt.subplots(2, 2, figsize=(11.25, 8))
    cs1 = axes[0, 0].contourf(X, Y, np.array(Pmpp) / 10, 100, cmap=cm.jet)
    axes[0, 0].set_xlabel(all_data[0]['x_axis_name'])
    axes[0, 0].set_ylabel(all_data[0]['y_axis_name'])
    # axes[0, 0].set_yscale("log")
    # axes[0, 0].set_xscale("log")
    axes[0, 0].set_title("Efficiency %")
    cbar1 = fig2.colorbar(cs1)

    cs2 = axes[0, 1].contourf(X, Y, abs(Isc), 100, cmap=cm.jet, locator=ticker.LogLocator())
    axes[0, 1].set_xlabel(all_data[0]['x_axis_name'])
    axes[0, 1].set_ylabel(all_data[0]['y_axis_name'])
    # axes[0, 1].set_yscale("log")
    # axes[0, 1].set_xscale("log")
    axes[0, 1].set_title("short circuit current A/cm$^{2}$")
    cbar2 = fig2.colorbar(cs2)

    cs3 = axes[1, 0].contourf(X, Y, abs(Voc), 100, cmap=cm.jet)
    axes[1, 0].set_xlabel(all_data[0]['x_axis_name'])
    axes[1, 0].set_ylabel(all_data[0]['y_axis_name'])
    # axes[1, 0].set_yscale("log")
    # axes[1, 0].set_xscale("log")
    axes[1, 0].set_title("Open circuit voltage V")
    cbar3 = fig2.colorbar(cs3)

    cs4 = axes[1, 1].contourf(X, Y, abs(FF) * 100, 100, cmap=cm.jet)
    axes[1, 1].set_xlabel(all_data[0]['x_axis_name'])
    axes[1, 1].set_ylabel(all_data[0]['y_axis_name'])
    # axes[1, 1].set_yscale("log")
    # axes[1, 1].set_xscale("log")
    axes[1, 1].set_title("Fill Factor")
    cbar4 = fig2.colorbar(cs4)

    fig2.suptitle(f"{version}")
    # plt.tight_layout()
    # fig1.legend()
    # plt.legend()
    fig2.savefig(f'performance_{version}.png', dpi=300)

    save_file_direction(f'{version}', f'{version}', saveing_data=all_data)

    movefile(f'performance_{version}.png', f'{version}')
    # movefile(f'carrier_distribution{version}.html', f'{version}')

    # movefile
    print('save complete')
