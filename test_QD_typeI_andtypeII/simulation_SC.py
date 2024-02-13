from solcore.light_source import LightSource
from solcore.solar_cell_solver import solar_cell_solver
import matplotlib.pyplot as plt
import os
import shutil
# from material_and_layer_QD import solar_each_size
from material_and_layer_QD import (QDSC_InSb
                                , solar_cell_InSb_and_GaSb_sweep_interlayer, solar_cell_InSb_and_GaSb_sweep_n)
from material_of_InSb_GaSb import QDSC_InSb_and_GaSb_barrier_mod

import numpy as np
from save_picture import schrodinger_graph_LDOS
import pickle
import csv
#========================================================================
#setup


def progresstion(progress, point):
    print('==============================================================================================================================')
    print('==============================================================================================================================')
    print( progress/point*100, f'{progress} / {point}')
    print('==============================================================================================================================')
    print('==============================================================================================================================')

def back_up_data(data, version):
    with open(f'{version}.pkl', 'wb') as fin:
        pickle.dump(data, fin)
        print('dictionary saved successfully to file')
def create_folder(create_folder):
    import os
    current_path = os.getcwd()
    # print(current_path)
    current_path = os.path.join(current_path, create_folder)
    print(current_path)
    if not os.path.exists(create_folder):
        os.makedirs(create_folder)
        print('create folder success')

def save_tuple2text(text, name, *data):  # each data ==> tuple(name, detail)
    text += name + '\nCustum text version' + '\n'
    text += "===============================START======================================= \n"
    for i in data:
        text += str(i) +'\n'
    text += "================================END======================================= \n"
    return text  # list_structure data topic and keyword

def save_full_solar_cells(text, solar_cells, name_solar):
    text += name_solar + 'Full text version' + '\n'
    text += "===============================START======================================= \n"
    for i in solar_cells:
        text += str(i) + '\n'
    text += "================================END======================================= \n"
    return text

def save_file_direction(save_folder, list_structure, name_text):  # find from current file
    import os
    current_path = os.getcwd()
    current_path = os.path.join(current_path, save_folder)
    if not os.path.exists(current_path):
        os.makedirs(current_path)
        print(f'create {current_path} folder ')
    complete_Name = os.path.join(current_path, name_text + ".txt")
    with open(complete_Name, 'w') as fin:
        for item in list_structure:
            fin.write(str(item) + '\n')
    print('save success')

def save_all_file_0d(data, version, con , list_structure=[]):
    fig, ax1 = plt.subplots(1, 1, figsize=(6, 4))

    ax1.semilogy(wl * 1e9, data["absorbed"][0], label=f"Total Absorbed")
    ax1.legend(loc="upper right", frameon=False)
    ax1.set_xlabel("Wavelength (nm)")
    ax1.set_ylabel("EQE")
    ax1.set_ylim(1e-6, 1.1)
    ax1.set_xlim(350, 1100)
    plt.tight_layout()
    # !!!   Change  !!!
    # !!!   Change  !!!
    # !!!   Change  !!!

    fig1, axes = plt.subplots(2, 2, figsize=(11.25, 8))

    axes[0, 0].semilogx(con, np.array(data["Pmpp"]) / 10/ con, "r-o")
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
    plt.tight_layout()

    # !!!   Change  !!!
    # !!!   Change  !!!
    # !!!   Change  !!!

    fig2, axIV = plt.subplots(1, 1, figsize=(6, 4))
    count = 0
    for i in data["allI"]:
        axIV.plot(-V, i / -10, label=f"x = Concentration (suns) = {con[count]}")
        count += 1

    axIV.set_ylim(0, 1e5)
    axIV.set_xlim(0, 1.5)
    axIV.set_xlabel("Voltage (V)")
    axIV.set_ylabel("J$_{SC}$ (mA/cm$^{2}$)")
    plt.tight_layout()

    fig2.savefig(f'IV_curve_{version}.png', dpi=300)
    fig1.savefig(f'performance_{version}.png', dpi=300)
    fig.savefig(f'EQE_{version}.png', dpi=300)

    save_file_direction(f'data_of_{version}', list_structure, f'{version}')

    def movefile(file,direction):
        save_path = os.path.join(current_path, direction)
        fig1_loc = os.path.join(current_path, file)
        fig1_loc_new = os.path.join(save_path, file)
        shutil.move(fig1_loc, fig1_loc_new)

    current_path = os.getcwd()
    movefile(f'IV_curve_{version}.png', f'data_of_{version}')
    movefile(f'performance_{version}.png', f'data_of_{version}')
    movefile(f'EQE_{version}.png', f'data_of_{version}')
    print('save complete')

def save_set_of_data(set_of_data, version, con, list_structure=[]):
    fig, ax1 = plt.subplots(1, 1, figsize=(6, 4))
    fig1, axes = plt.subplots(2, 2, figsize=(11.25, 8))
    fig2, axIV = plt.subplots(1, 1, figsize=(8, 6))
    fig3, axCar = plt.subplots(len(set_of_data), 1, figsize=(5*len(set_of_data), 8))
    num = 0
    for data in set_of_data:

        print(data)

        ax1.plot(wl * 1e9, data["absorbed"][0], label=f"Total Absorbed mode = {data['mode']} ")
        ax1.legend(loc="upper right", frameon=False)
        ax1.set_xlabel("Wavelength (nm)")
        ax1.set_ylabel("EQE")
        ax1.set_ylim(0, 1.1)
        ax1.set_xlim(350, 1200)
        plt.tight_layout()

        # linestyle = ["-", "--", ":", "-."]
        marker = [".", ",", "o", 'v', "^", "<", ">", "s", "p", "*", "h", "+", "x", "D", "d" ]
        blue = [
            (0, 0, 1, 0.1),  # Very light blue
            (0, 0, 1, 0.3),  # Light blue
            (0, 0, 1, 0.5),  # Medium blue
            (0, 0, 1, 0.7),  # Dark blue
            (0, 0, 1, 0.9),  # Very dark blue
            (0, 0, 1, 1.0),  # Full blue
            (0, 0, 1, 1.0)  # Full blue, repeated to have 7 colors
        ]
        red = [
            (1, 0, 0, 0.5),
            (1, 0.5, 0.5, 0.5),
            (1, 0, 0.5, 0.5),
            (1, 0.5, 0, 0.5),
            (1, 0.5, 0.5, 0.5),
            (1, 0.5, 0, 0.5),
            (1, 0.5, 0, 0.5)
        ]
        green = [
            (0, 1, 0, 0.5),
            (0, 1, 0.5, 0.5),
            (0, 0.5, 0, 0.5),
            (0, 0.5, 0.5, 0.5),
            (0, 0, 0.5, 0.5),
            (0, 0.5, 0.5, 0.5),
            (0, 1, 0, 0.5)
        ]
        black = [
            (0, 0, 0, 0.5),
            (0, 0, 0.5, 0.5),
            (0, 0.5, 0.5, 0.5),
            (0, 0.5, 0, 0.5),
            (0, 0, 0.5, 0.5),
            (0, 0, 0.5, 0.5),
            (0, 0, 0, 0.5)
        ]
        # print(data)
        axes[0, 0].semilogx(con, np.array(data["Pmpp"]) / 10/ con, color=red[num], marker=marker[num], label=f"{data['mode']}")
        axes[0, 0].set_xlabel("Concentration (suns)")
        axes[0, 0].set_ylabel("Efficiency (%)")

        axes[0, 1].loglog(con, abs(np.array(data["Isc"])), color=blue[num], marker=marker[num], label=f"{data['mode']}")
        axes[0, 1].set_xlabel("Concentration (suns)")
        axes[0, 1].set_ylabel("I$_{SC}$ (Am$^{-2}$)")

        axes[1, 0].semilogx(con, abs(np.array(data["Voc"])), color=green[num], marker=marker[num], label=f"{data['mode']}")
        axes[1, 0].set_xlabel("Concentration (suns)")
        axes[1, 0].set_ylabel("V$_{OC}$ (V)")

        axes[1, 1].semilogx(con, abs(np.array(data["FF"])) * 100,color=black[num], marker=marker[num], label=f"{data['mode']}")
        axes[1, 1].set_xlabel("Concentration (suns)")
        axes[1, 1].set_ylabel("Fill Factor (%)")
        fig1.suptitle(f"{version}")
        plt.tight_layout()
        fig1.legend()

        for count, i in enumerate(data["allI"]):
            axIV.plot(-V, i / -10, label=f"x = Concentration (suns) = {con[count]} mode = {data['mode']}")

        axIV.set_ylim(0, 1e5)
        axIV.set_xlim(0, 1.5)
        axIV.set_xlabel("Voltage (V)")
        axIV.set_ylabel("J$_{SC}$ (mA/cm$^{2}$)")
        plt.tight_layout()
        plt.legend()
        try:
            axCar[num, 0].semilogy(data["xsc"]*1e9, data["nsc"], 'b', label=f"{data['mode']}")
            axCar[num, 0].semilogy(data["xsc"]*1e9, data["psc"], 'r', label=f"{data['mode']}")
            axCar[num, 0].semilogy(data["xeq"]*1e9, data["neq"], 'b--', label=f"{data['mode']}")
            axCar[num, 0].semilogy(data["xeq"]*1e9, data["peq"], 'r--', label=f"{data['mode']}")
        except:
            pass
        num += 1

    plt.legend()
    fig.savefig(f'EQE_{version}.png', dpi=300)
    fig1.savefig(f'performance_{version}.png', dpi=300)
    fig2.savefig(f'IV_curve_{version}.png', dpi=300)
    save_file_direction(f'data_of_{version}', list_structure, f'{version}')

    def movefile(file, direction):
        save_path = os.path.join(current_path, direction)
        fig1_loc = os.path.join(current_path, file)
        fig1_loc_new = os.path.join(save_path, file)
        shutil.move(fig1_loc, fig1_loc_new)

    current_path = os.getcwd()
    movefile(f'IV_curve_{version}.png', f'data_of_{version}')
    movefile(f'performance_{version}.png', f'data_of_{version}')
    movefile(f'EQE_{version}.png', f'data_of_{version}')
    print('save complete')

def defultsave(solarcell, saveaddrest, version, save=True):
    defult_saving = ["Isc", "Voc", "FF", "Pmpp"]
    for i in defult_saving:
        saveaddrest[f"{i}"].append(solarcell.iv[f"{i}"])
    saveaddrest["allI"].append(solarcell.iv["IV"][1])

    if save:
        with open(f'{version}.pkl', 'wb') as fin:
            pickle.dump(saveaddrest, fin)
            print('dictionary saved successfully to file')
    return saveaddrest

def save_ligth(solarcell, saveaddrest, version,save=True):
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

#light
wl = np.linspace(350, 1200, 401) * 1e-9
light_source = LightSource(
    source_type="standard",
    version="AM1.5g",
    x=wl,
    output_units="photon_flux_per_m",
    concentration=1,
)


#condition
# !!!   Change  !!!
# !!!   Change  !!!
#
# con = con_GaInP_active
# con1 = con_AlInP_top
# con2 = con_GaInP_active
# !!!   Change  !!!
# !!!   Change  !!!


vint = np.linspace(-3.5, 4, 600)
# V = np.linspace(-3.5, 3.5, 300)
# V = np.linspace(0,3.5,300) # pn
V = np.linspace(-1.5,0,300) # np
con_light = np.logspace(0, 3, 5)


data = {"allI":[],
        "Isc":[],
        "Voc":[],
        "FF":[],
        "Pmpp":[],
        "absorbed":[],
        "xsc":[],
        "nsc":[],
        "psc":[],
        "xeq":[],
        "neq":[],
        "peq":[],
        }
deta_mode = {
        "allI":[],
        "Isc" :[],
        "Voc" :[],
        "FF"  :[],
        "Pmpp":[],
        "absorbed" :[],
        "mode":[],
        "xsc":[],
        "nsc":[],
        "psc":[],
        "xeq":[],
        "neq":[],
        "peq":[],
}
set_of_data = []

#
#========================================================================
# simulation 0d
# EQE
# version = 'QDSC_InSb_and_GaSb_barrier_mod'
# sim_mat = QDSC_InSb_and_GaSb_barrier_mod()
def simulation0D(version, sim_mat):
    list_structure = [str(i) for i in sim_mat]
    solar_cell_solver(sim_mat, "qe",
                              user_options={"light_source": light_source,
                                            "wavelength": wl,
                                            "optics_method": "TMM",}, )
    data = save_ligth(sim_mat, data, version)
    for i in con_light:
        light_source.concentration = i
        # IV
        solar_cell_solver(sim_mat,"iv"
                              ,user_options={"light_source": light_source,
                                             "wavelength": wl,
                                             "optics_method": None,
                                             "light_iv": True,
                                             "mpp": True,
                                             "voltages": V,
                                             "internal_voltages": vint,
                                    },)

        data = defultsave(sim_mat, data, version)
    return data, list_structure
# #========================================================================
# # #simulation 1D
version = "QDSC_InSb_and_GaSb_barrier_mod"
sim_mat = QDSC_InSb_and_GaSb_barrier_mod()
def simulation1D(version, sim_mat):
    list_structure = []
    for size, cell in sim_mat.items():
        data_mode = dict(allI=[], Isc=[], Voc=[], FF=[], Pmpp=[], absorbed=[], mode=size, xsc=[], nsc=[], psc=[], xeq=[],
                         neq=[], peq=[])
        list_structure.append("start item ================================================================================")
        for i in cell:
            list_structure.append(str(i))
        list_structure.append("end item   ================================================================================")
        solar_cell_solver(cell, "qe",
                          user_options={"light_source": light_source,
                                        "wavelength": wl,
                                        "optics_method": "TMM", }, )
        data_mode = save_ligth(cell, data_mode, version, save=False)
        for i in con_light:
            light_source.concentration = i
            #IV
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
    return set_of_data, list_structure
set_of_data, list_structure = simulation1D(version, sim_mat)
#========================================================================
#show
#
# data = load_old_data("solar_cell_InSb_and_GaSb_pin.pkl")
# set_of_data = load_old_data("QDSC_InSb_and_GaSb_barrier_mod.pkl")
# # print(set_of_data)
# # 'kp8x8_bulk', "strain", "relaxed"
# a =  ["mode=kp8x8_bulk", "mode=strain", "mode=relaxed"]
# for count, i in enumerate(set_of_data):
#     # i['mode'] = f"dot size = {a[count]}"
#     print(count)
#     print(i)
# !!!   Change  !!!
# !!!   Change  !!!

# save_all_file_0d(data, version,  con_light, list_structure=list_structure )
save_set_of_data(set_of_data, version, con_light, list_structure=list_structure)




# !!!   Change  !!!
# !!!   Change  !!!

plt.show()