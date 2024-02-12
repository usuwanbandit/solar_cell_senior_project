import numpy as np
from solcore.light_source import LightSource
from solcore.solar_cell_solver import solar_cell_solver
import matplotlib.pyplot as plt
import os
import shutil
from material_and_layer import (my_solar_cell, vary_GaInP, vary_AlInP, con_AlInP, con_GaInP , vary_AlInP_and_GaInP,
                                solat_cell_with_arc, GaInP_solar_cell, vary_AlInP_top ,con_AlInP_top, vary_AlInP_bottom, con_AlInP_bottom
                                ,vary_AlInP_active, con_GaInP_active, vary_AlInP_active_and_passive )
import pickle
#========================================================================
#setup
def progresstion(progress, point):
    print('==============================================================================================================================')
    print('==============================================================================================================================')
    print( progress/point*100, f'{progress} / {point}')
    print('==============================================================================================================================')
    print('==============================================================================================================================')


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
    return text  # note data topic and keyword


def save_full_solar_cells(text, solar_cells, name_solar):
    text += name_solar + 'Full text version' + '\n'
    text += "===============================START======================================= \n"
    for i in solar_cells:
        text += str(i) + '\n'
    text += "================================END======================================= \n"
    return text


def save_file_direction(save_folder, text, name_text):  # find from current file
    import os
    current_path = os.getcwd()
    current_path = os.path.join(current_path, save_folder)
    if not os.path.exists(current_path):
        os.makedirs(current_path)
        print(f'create {current_path} folder ')
    complete_Name = os.path.join(current_path, name_text + ".txt")
    file1 = open(complete_Name, "w")
    toFile = text
    file1.write(toFile)
    file1.close()
    print('save success')

def save_all_file_0d(data, version):
    fig, ax1 = plt.subplots(1, 1, figsize=(6, 4))

    count = 0
    for i in data["absorbed"]:
        ax1.plot(wl * 1e9, i, label=f"Total Absorbed{con[count]}")
        count += 1
    ax1.legend(loc="upper right", frameon=False)
    ax1.set_xlabel("Wavelength (nm)")
    ax1.set_ylabel("EQE")
    ax1.set_ylim(0, 1.1)
    ax1.set_xlim(350, 1200)
    plt.tight_layout()

    fig2, axIV = plt.subplots(1, 1, figsize=(6, 4))
    count = 0
    for i in data["allI"]:
        axIV.plot(-V, i / -10, label=f"x = {con[count]}")
        count += 1

    axIV.set_ylim(0, 30)
    axIV.set_xlim(0, 1.5)
    axIV.set_xlabel("Voltage (V)")
    axIV.set_ylabel("J$_{SC}$ (mA/cm$^{2}$)")
    plt.tight_layout()

    fig.savefig(f'IV_curve_{version}.png', dpi=300)
    fig2.savefig(f'EQE_{version}.png', dpi=300)
    save_file_direction(f'data_of_{version}', str(data), f'{version}')

    def movefile(file,direction):
        save_path = os.path.join(current_path, direction)
        fig1_loc = os.path.join(current_path, file)
        fig1_loc_new = os.path.join(save_path, file)
        shutil.move(fig1_loc, fig1_loc_new)

    current_path = os.getcwd()
    movefile(f'IV_curve_{version}.png', f'data_of_{version}')
    movefile(f'EQE_{version}.png', f'data_of_{version}')
    print('save complete')


def save_all_file_1d(data, version, con):
    fig, ax1 = plt.subplots(1, 1, figsize=(6, 4))

    count = 0
    for i in data["absorbed"]:
        ax1.plot(wl * 1e9, i, label=f"Total Absorbed{con[count]}")
        count += 1
    ax1.legend(loc="upper right", frameon=False)
    ax1.set_xlabel("Wavelength (nm)")
    ax1.set_ylabel("EQE")
    ax1.set_ylim(0, 1.1)
    ax1.set_xlim(350, 1200)
    plt.tight_layout()
    # !!!   Change  !!! 
    # !!!   Change  !!! 
    # !!!   Change  !!! 

    fig1, axes = plt.subplots(2, 2, figsize=(11.25, 8))

    axes[0, 0].plot(con, np.array(data["pmpp"]) / 10, "r-o")
    axes[0, 0].set_xlabel("Ga$_{1-x}$In$_{x}$P")
    axes[0, 0].set_ylabel("Efficiency (%)")

    axes[0, 1].plot(con, abs(np.array(data["isc"])), "b-o")
    axes[0, 1].set_xlabel("Ga$_{1-x}$In$_{x}$P")
    axes[0, 1].set_ylabel("I$_{SC}$ (Am$^{-2}$)")

    axes[1, 0].plot(con, abs(np.array(data["voc"])), "g-o")
    axes[1, 0].set_xlabel("Ga$_{1-x}$In$_{x}$P")
    axes[1, 0].set_ylabel("V$_{OC}$ (V)")

    axes[1, 1].plot(con, abs(np.array(data["FF"])) * 100, "k-o")
    axes[1, 1].set_xlabel("Ga$_{1-x}$In$_{x}$P")
    axes[1, 1].set_ylabel("Fill Factor (%)")
    fig1.suptitle(f"{version}")
    plt.tight_layout()

    # !!!   Change  !!! 
    # !!!   Change  !!! 
    # !!!   Change  !!! 

    fig2, axIV = plt.subplots(1, 1, figsize=(6, 4))
    count = 0
    for i in data["allI"]:
        axIV.plot(-V, i / -10, label=f"x = {con[count]}")
        count += 1

    axIV.set_ylim(0, 30)
    axIV.set_xlim(0, 1.5)
    axIV.set_xlabel("Voltage (V)")
    axIV.set_ylabel("J$_{SC}$ (mA/cm$^{2}$)")
    plt.tight_layout()

    fig.savefig(f'IV_curve_{version}.png', dpi=300)
    fig1.savefig(f'performance_{version}.png', dpi=300)
    fig2.savefig(f'EQE_{version}.png', dpi=300)
    save_file_direction(f'data_of_{version}', str(data), f'{version}')

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


def save_all_file_2d(data, version, con1, con2):
    from numpy import ma
    from matplotlib import cm, ticker
    X, Y = np.meshgrid(con1, con2)
    eff = data["pmpp"] / light_source.power_density * 100
    fig2, axes = plt.subplots(2, 2, figsize=(16.875, 12))

    eff = ma.masked_where(eff <= 0, eff)
    cs1 = axes[0, 0].contourf(X, Y, eff, 100, cmap=cm.jet)
    axes[0, 0].set_xlabel("Ga$_{1-x}$In$_{x}$P")
    axes[0, 0].set_ylabel("Al$_{x}$In$_{1-x}$P")
    # axes[0, 0].set_yscale("log")
    # axes[0, 0].set_xscale("log")
    axes[0, 0].set_title("Efficiency %")
    cbar1 = fig2.colorbar(cs1)

    cs2 = axes[0, 1].contourf(X, Y, abs(np.array(data["isc"])), 100, cmap=cm.jet)
    axes[0, 1].set_xlabel("Ga$_{1-x}$In$_{x}$P")
    axes[0, 1].set_ylabel("Al$_{x}$In$_{1-x}$P")
    # axes[0, 1].set_yscale("log")
    # axes[0, 1].set_xscale("log")
    axes[0, 1].set_title("short circuit current A/cm$^{2}$")
    cbar2 = fig2.colorbar(cs2)


    cs3 = axes[1, 0].contourf(X, Y, abs(np.array(data["voc"])), 100, cmap=cm.jet)
    axes[1, 0].set_xlabel("Ga$_{1-x}$In$_{x}$P")
    axes[1, 0].set_ylabel("Al$_{x}$In$_{1-x}$P")
    # axes[1, 0].set_yscale("log")
    # axes[1, 0].set_xscale("log")
    axes[1, 0].set_title("Open circuit voltage V")
    cbar3 = fig2.colorbar(cs3)

    cs4 = axes[1, 1].contourf(X, Y, abs(np.array(data["FF"])) * 100, 100, cmap=cm.jet)
    axes[1, 1].set_xlabel("Ga$_{1-x}$In$_{x}$P")
    axes[1, 1].set_ylabel("Al$_{x}$In$_{1-x}$P")
    # axes[1, 1].set_yscale("log")
    # axes[1, 1].set_xscale("log")
    axes[1, 1].set_title("fill factor")
    cbar4 = fig2.colorbar(cs4)
    plt.tight_layout()
    fig2.savefig(f'performance_{version}.png', dpi=300)
    save_file_direction(f'data_of_{version}', str(data), f'{version}')
    def movefile(file, direction):
        save_path = os.path.join(current_path, direction)
        fig1_loc = os.path.join(current_path, file)
        fig1_loc_new = os.path.join(save_path, file)
        shutil.move(fig1_loc, fig1_loc_new)

    current_path = os.getcwd()
    movefile(f'performance_{version}.png', f'data_of_{version}')
    print('save complete')


def defultsave(solarcell, saveaddrest, version):
    saveaddrest["isc"].append(solarcell.iv["Isc"])
    saveaddrest["voc"].append(solarcell.iv["Voc"])
    saveaddrest["FF"].append(solarcell.iv["FF"])
    saveaddrest["pmpp"].append(solarcell.iv["Pmpp"])
    saveaddrest["allI"].append(solarcell.iv["IV"][1])
    saveaddrest["absorbed"].append(solarcell.absorbed)
    with open(f'{version}.pkl', 'wb') as fin:
        pickle.dump(saveaddrest, fin)
        print('dictionary saved successfully to file')
    return saveaddrest


def save_2D(solarcell, data, version, position):
    data['isc'][position] = solarcell.iv['Isc']
    data["isc"][position] = solarcell.iv["Isc"]
    data["voc"][position] = solarcell.iv["Voc"]
    data["FF"][position] = solarcell.iv["FF"]
    data["pmpp"][position] = solarcell.iv["Pmpp"]
    # data['isc'][position] =  solarcell
    # data["isc"][position] =  solarcell
    # data["voc"][position] =  solarcell
    # data["FF"][position] =  solarcell
    # data["pmpp"][position] = solarcell
    with open(f'{version}.pkl', 'wb') as fin:
        pickle.dump(data, fin)
        print('dictionary saved successfully to file')
    return data

def load_old_data(version):
    with open(f'{version}', 'rb') as fp:
        data = pickle.load(fp)
    print('Loading dictionary complete')
    print(data["allI"])
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

con = con_GaInP_active
con1 = con_AlInP_top
con2 = con_GaInP_active
# !!!   Change  !!! 
# !!!   Change  !!! 


vint = np.linspace(-3.5, 4, 600)
V = np.linspace(-3.5, 0, 300)
data = {"allI":[],
        "isc":[],
        "voc":[],
        "FF":[],
        "pmpp":[],
        "absorbed":[],
        }

data_2d = {
        "isc":np.zeros((len(con2), len(con1))),
        "voc":np.zeros((len(con2), len(con1))),
        "FF":np.zeros((len(con2), len(con1))),
        "pmpp":np.zeros((len(con2), len(con1))),

        }
# print(data_2d)
point = len(con2)* len(con1)

#========================================================================
#simulation 0d
# EQE
solar_cell_solver(GaInP_solar_cell, "qe",
                      user_options={"light_source": light_source,
                                    "wavelength": wl,
                                    "optics_method": "TMM",}, )
# IV
solar_cell_solver(GaInP_solar_cell,"iv"
                      ,user_options={"light_source": light_source,
                                     "wavelength": wl,
                                     "optics_method": None,
                                     "light_iv": True,
                                     "mpp": True,
                                     "voltages": V,
                                     "internal_voltages": vint,
                            },)
data = defultsave(GaInP_solar_cell, data, 'GaInPa_solar_cells')
#========================================================================

# #varysim 1d
# for i in vary_AlInP_active:
#     #simulation
#     # EQE
#     solar_cell_solver(i, "qe",
#                           user_options={"light_source": light_source,
#                                         "wavelength": wl,
#                                         "optics_method": "TMM",}, )
#     #IV
#     solar_cell_solver(i,"iv"
#                           ,user_options={"light_source": light_source,
#                                          "wavelength": wl,
#                                          "optics_method": None,
#                                          "light_iv": True,
#                                          "mpp": True,
#                                          "voltages": V,
#                                          "internal_voltages": vint,
#                                 },)
#     data = defultsave(i, data, 'GaInPa_solar_cells_vary_active')
# # #=========================================================================
# #sim2d
# count1 = 0
# count2 = 0
# progress = 0
#
# for inline_barrier in vary_AlInP_active_and_passive:
#     for i in inline_barrier:
#         solar_cell_solver(i, "qe",
#                           user_options={"light_source": light_source,
#                                         "wavelength": wl,
#                                         "optics_method": "TMM", }, )
#
#         # IV
#         solar_cell_solver(i, "iv"
#                           , user_options={"light_source": light_source,
#                                           "wavelength": wl,
#                                           "optics_method": None,
#                                           "light_iv": True,
#                                           "mpp": True,
#                                           "voltages": V,
#                                           "internal_voltages": vint,
#                                           }, )
#         # num += 1
#         save_2D(i,data_2d, 'vary_AlInP_active_and_ passive', (count1, count2))
#         progresstion(progress, point)
#         progress += 1
#         count2 += 1
#
#     count2 = 0
#     count1 += 1
#========================================================================
#show

# data = load_old_data("GaInPa_solar_cells_vary_active.pkl")



# !!!   Change  !!!
# !!!   Change  !!!

save_all_file_0d(data, 'GaInPa_solar_cells')

# save_all_file_1d(data, 'GaInPa_solar_cells_vary_active', con_GaInP_active)
# save_all_file_2d(data_2d, 'vary_AlInP_active_and_passive', con1, con2)


# !!!   Change  !!!
# !!!   Change  !!!

plt.show()