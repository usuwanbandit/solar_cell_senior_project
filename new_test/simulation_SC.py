import time

import matplotlib.pyplot as plt
import numpy as np
from solcore.light_source import LightSource
from solcore.solar_cell_solver import solar_cell_solver
# import matplotlib.pyplot as plt
import os
import shutil
from material_and_layer_QD import *
from material_of_InSb_GaSb import *
from scipy.integrate import trapz
# from save_picture import schrodinger_graph_LDOS
import pickle
import tkinter as tk
from tkinter import messagebox
import mpld3


# ========================================================================
# setup

def show_warning(text):
    messagebox.showwarning("time taking", text)
def sec_to_hms(seconds):
    # Calculate hours, minutes, and seconds
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return hours, minutes, seconds


def back_up_data(data, version):
    with open(f'{version}.pkl', 'wb') as fin:
        pickle.dump(data, fin)
        print('dictionary saved successfully to file')


def create_folder(folder):
    import os
    current_path = os.getcwd()
    # print(current_path)
    current_path = os.path.join(current_path, folder)
    print(current_path)
    if not os.path.exists(folder):
        os.makedirs(folder)
        print('create folder success')

def get_identical_colors(colormap, num_colors):
    # Create a normalized array of indices
    indices = np.linspace(0, 1, num_colors)
    # Get the same color for all indices
    cmap_colors = colormap(indices)[:, :3]  # Extract RGB values
    return cmap_colors

def save_file_direction(save_folder, name_text, saveing_data=list()):  # find from current file
    import os
    current_path = os.getcwd()
    current_path = os.path.join(current_path, save_folder)
    if not os.path.exists(current_path):
        os.makedirs(current_path)
        print(f'create {current_path} folder ')
    complete_Name = os.path.join(current_path, name_text + ".txt")
    with open(complete_Name, 'w') as fin:
        for item in saveing_data:
            try:
                fin.write(str(item["note"]) + '\n')
            except:
                print('this file have not note')
                pass
            try:
                for layer in item['list_structure']:
                    fin.write(str(layer) + '\n')
            except:
                print('this file have not list_structure')
                pass
    print('save success')


def save_all_file_0d(data, version, con):
    fig, ax1 = plt.subplots(1, 1, figsize=(6, 4))
    fig3, axCar = plt.subplots(1, 1, figsize=(16, 5))

    ax1.plot(wl * 1e9, data["absorbed"][0], label=f"Total Absorbed")
    ax1.legend(loc="upper right", frameon=False)
    ax1.set_xlabel("Wavelength (nm)")
    ax1.set_ylabel("EQE")
    ax1.set_ylim(0, 1.1)
    ax1.set_xlim(350,1200)
    plt.legend()
    plt.tight_layout()


    fig1, axes = plt.subplots(2, 2, figsize=(11.25, 8))

    axes[0, 0].semilogx(con, np.array(data["Pmpp"]) * 100 / get_ligth_power(con=con), "r-o")
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
    axIV.set_ylabel("J$_{SC}$ (mA/cm$^{2}$)")
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

    def movefile(file, direction):

        save_path = os.path.join(current_path, direction)
        fig1_loc = os.path.join(current_path, file)
        fig1_loc_new = os.path.join(save_path, file)
        shutil.move(fig1_loc, fig1_loc_new)

    current_path = os.getcwd()
    movefile(f'IV_curve_{version}.png', f'{version}')
    movefile(f'performance_{version}.png', f'{version}')
    movefile(f'EQE_{version}.png', f'{version}')
    print('save complete')

def movefile(file, direction):
    current_path = os.getcwd()
    save_path = os.path.join(current_path, direction)
    fig1_loc = os.path.join(current_path, file)
    fig1_loc_new = os.path.join(save_path, file)
    shutil.move(fig1_loc, fig1_loc_new)

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
        color = [plt.cm.hsv(i /len(set_of_data)) for i in range(len(set_of_data))]

        axes[0, 0].semilogx(con, np.array(data["Pmpp"]) / con/ 10, color=color[num],label=f"{data['mode']}")
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
            axIV.plot(-V, i / data["Isc"][count], label=f"x = Concentration (suns) = {con[count]} mode = {data['mode']}")

        axIV.set_ylim(0, 1.5)
        axIV.set_xlim(0, 1.5)
        axIV.set_xlabel("Voltage (V)")
        axIV.set_ylabel("J$_{SC}$ (mA/cm$^{2}$)")
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

def save_set_of_data_sun_constant(set_of_data, version, note_from_mat):
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
        color = [plt.cm.hsv(i /len(set_of_data)) for i in range(len(set_of_data))]

        axes[0, 0].semilogx(note_from_mat['plot_x'], np.array(data["Pmpp"])  / 10, color=color[num],label=f"{data['mode']}")
        axes[0, 0].set_xlabel(note_from_mat['labelx'])
        axes[0, 0].set_ylabel("Efficiency (%)")

        axes[0, 1].loglog(note_from_mat['plot_x'], abs(np.array(data["Isc"])), color=color[num])
        axes[0, 1].set_xlabel(note_from_mat['labelx'])
        axes[0, 1].set_ylabel("I$_{SC}$ (Am$^{-2}$)")

        axes[1, 0].semilogx(note_from_mat['plot_x'], abs(np.array(data["Voc"])), color=color[num])
        axes[1, 0].set_xlabel(note_from_mat['labelx'])
        axes[1, 0].set_ylabel("V$_{OC}$ (V)")

        axes[1, 1].semilogx(note_from_mat['plot_x'], abs(np.array(data["FF"])) * 100, color=color[num])
        axes[1, 1].set_xlabel(note_from_mat['labelx'])
        axes[1, 1].set_ylabel("Fill Factor (%)")

        fig1.suptitle(f"{version}")
        plt.tight_layout()
        fig1.legend()


        for count, i in enumerate(data["allI"]):
            axIV.plot(-V, i / data["Isc"][count], label=f"{note_from_mat['labelx']} mode = {data['mode']}")

        axIV.set_ylim(0, 1.5)
        axIV.set_xlim(0, 1.5)
        axIV.set_xlabel("Voltage (V)")
        axIV.set_ylabel("J$_{SC}$ (mA/cm$^{2}$)")
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


# light
# wl = np.linspace(300, 3000, 700) * 1e-9
wl = np.linspace(350, 1200, 401)*1e-9 # version1
light_source = LightSource(source_type="standard"
                           , version="AM1.5g"
                           , x=wl
                           , output_units="photon_flux_per_m"
                           , concentration=1
                           )
light_source_measure = LightSource(
    source_type="standard",
    version="AM1.5g",
    output_units='power_density_per_m',
    x=wl,
    concentration=1,
)


def get_ligth_power(con=None, source_type="standard", version="AM1.5g", ):
    power_con = None
    if isinstance(con, list) or isinstance(con, np.ndarray):
        buffer = []
        for i in con:
            light_source_measure = LightSource(
                source_type=source_type,
                version=version,
                output_units='power_density_per_m',
                x=wl,
                concentration=i, )
            spectrum = light_source_measure.spectrum()
            power_buffer = trapz(spectrum, wl)  #
            buffer.append(power_buffer[1])
        power_con = np.array(buffer)
    elif isinstance(con, int):
        light_source_measure = LightSource(
            source_type=source_type,
            version=version,
            output_units='power_density_per_m',
            x=wl,
            concentration=con, )
        spectrum = light_source_measure.spectrum()
        power_con = trapz(spectrum, wl)[1]  #
    return power_con  # W/m2



vint = np.linspace(-3.5, 4, 600)
# V = np.linspace(-3.5, 3.5, 300)
# V = np.linspace(0,3.5,300) # pn
V = np.linspace(-1.5, 0, 300)  # np
con_light = np.logspace(0, 3, 5)
# con_light = np.linspace(1, 2, 5)

data = {"allI": [],
        "Isc": [],
        "Voc": [],
        "FF": [],
        "Pmpp": [],
        "absorbed": [],
        "xsc": [],
        "nsc": [],
        "psc": [],
        "xeq": [],
        "neq": [],
        "peq": [],
        }
deta_mode = {
    "allI": [],
    "Isc": [],
    "Voc": [],
    "FF": [],
    "Pmpp": [],
    "absorbed": [],
    "mode": [],
    "xsc": [],
    "nsc": [],
    "psc": [],
    "xeq": [],
    "neq": [],
    "peq": [],
}
set_of_data = []


#
# ========================================================================
# simulation 0d
def simulation0D(version, sim_mat, note=''):
    data = {"allI": [], "Isc": [], "Voc": [], "FF": [], "Pmpp": [], "absorbed": [], "xsc": [], "nsc": [], "psc": [],
            "xeq": [], "neq": [], "peq": [], "note": note, 'list_structure': [str(i) for i in sim_mat]}

    solar_cell_solver(sim_mat, "qe",
                      user_options={"light_source": light_source,
                                    "wavelength": wl,
                                    "optics_method": "TMM", }, )
    data = save_ligth(sim_mat, data, version)
    for i in con_light:
        light_source.concentration = i
        # IV
        solar_cell_solver(sim_mat, "iv"
                          , user_options={"light_source": light_source,
                                          "wavelength": wl,
                                          "optics_method": None,
                                          "light_iv": True,
                                          "mpp": True,
                                          "voltages": V,
                                          "internal_voltages": vint,
                                          }, )
        data = defultsave(sim_mat, data, version)
    return data


# #========================================================================
# # #simulation 1D
def simulation1D(version, sim_mat, note=''):
    for size, cell in sim_mat.items():
        data_mode = dict(allI=[], Isc=[], Voc=[], FF=[], Pmpp=[], absorbed=[], mode=size, xsc=[], nsc=[], psc=[],
                         xeq=[], neq=[], peq=[], note=note, list_structure=[])
        data_mode['list_structure'].append(
            "start item ================================================================================")
        _ = [data_mode['list_structure'].append(str(i)) for i in cell]
        data_mode['list_structure'].append(
            "end item   ================================================================================")
        solar_cell_solver(cell, "qe",
                          user_options={"light_source": light_source,
                                        "wavelength": wl,
                                        "optics_method": "TMM", }, )
        data_mode = save_ligth(cell, data_mode, version, save=False)
        for i in con_light:
            light_source.concentration = i
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
            data_mode = defultsave(cell, data_mode, version, save=False)

        set_of_data.append(data_mode)
        back_up_data(set_of_data, version)
    return set_of_data

def simulation1D_sun_constant(version, sim_mat, note=''):
    for size, cell in sim_mat.items():
        data_mode = dict(allI=[], Isc=[], Voc=[], FF=[], Pmpp=[], absorbed=[], mode=size, xsc=[], nsc=[], psc=[],
                         xeq=[], neq=[], peq=[], note=note, list_structure=[])
        data_mode['list_structure'].append(
            "start item ================================================================================")
        _ = [data_mode['list_structure'].append(str(i)) for i in cell]
        data_mode['list_structure'].append(
            "end item   ================================================================================")
        solar_cell_solver(cell, "qe",
                          user_options={"light_source": light_source,
                                        "wavelength": wl,
                                        "optics_method": "TMM", }, )
        data_mode = save_ligth(cell, data_mode, version, save=False)
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
        data_mode = defultsave(cell, data_mode, version, save=False)

        set_of_data.append(data_mode)
        back_up_data(set_of_data, version)
    return set_of_data

# ========================================================================
# show
#
def sim0D():
    start = time.perf_counter()
    version = "ref_GaAs"
    sim_mat = ref_GaAs()
    note = 'reference solar cell of compare differance between no dot and dot'
    data = simulation0D(version, sim_mat, note=note)
    stop = time.perf_counter()
    hours, minutes, seconds = sec_to_hms(stop - start)
    print(f"this run take time {hours}h/{minutes}min/{seconds}sec")
    root = tk.Tk()
    root.withdraw()
    show_warning(f"this run take time {hours} hours/ {minutes} minutes/ {seconds} seconds")
    save_all_file_0d(data, version, con_light)
    movefile(f'Carrier_distribution_{version}.html', f'{version}')

    root.update()




def sim1D():
    start = time.perf_counter()
    version = "InSb_dot_size"
    sim_mat, note_mat = InSb_dot_size()
    note = 'insert InSb dot in GaAs ref that have verier dot size'
    set_of_data = simulation1D(version, sim_mat, note=note)
    stop = time.perf_counter()
    hours, minutes, seconds = sec_to_hms(stop - start)
    print(f"this run take time {hours} hours/ {minutes} minutes/ {seconds} seconds")
    root = tk.Tk()
    root.withdraw()
    save_set_of_data(set_of_data, version, con_light)
    movefile(f'Carrier_distribution_{version}.html', f'{version}')

    show_warning(f"this run take time {hours} hours/ {minutes} minutes/ {seconds} seconds")
    root.update()




def load(version, is1D=False, ):
    if is1D:
        set_of_data = load_old_data("QDSC_InSb_and_GaSb_barrier_mod.pkl")
        save_set_of_data(set_of_data, version, con_light)
        movefile(f'Carrier_distribution_{version}.html', f'{version}')

    else:
        data = load_old_data('QDSC_InAs_GaSb_under_interlayer.pkl')
        save_all_file_0d(data, version, con_light)
        movefile(f'Carrier_distribution_{version}.html', f'{version}')




def main():
    sim1D()
    # load("QDSC_InSb_and_GaSb_barrier_mod", is1D=True)

if __name__ == "__main__":
    main()
    # plt.show()

