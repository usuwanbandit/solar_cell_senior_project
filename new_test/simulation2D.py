# import matplotlib.pyplot as plt
# import numpy as np
from solcore.light_source import LightSource
from solcore.solar_cell_solver import solar_cell_solver
from simulation_SC import *
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
from numpy import ma
from matplotlib import cm, ticker

def simulation1D_sun_constant(version, sim_mat, plot_note, note=''):
    all_data = []
    for mode_y, x_axis in sim_mat.items():
        set_of_data = []
        for mode_x, cell in x_axis.items():
            data_mode = dict(allI=[], Isc=[], Voc=[], FF=[], Pmpp=[], absorbed=[], mode_x=mode_x, mode_y=mode_y, xsc=[], nsc=[], psc=[],
                             xeq=[], neq=[], peq=[], note=note, list_structure=[], x_axis=plot_note['x_axis'], x_axis_name=plot_note["x_axis_name"]
                             ,  y_axis=plot_note['y_axis'], y_axis_name=plot_note["y_axis_name"])
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
        all_data.append(set_of_data)
        back_up_data(all_data,version)
    return all_data

def save_set_of_data_sun_constant_2D(all_data, version):
    Pmpp = []
    Isc = []
    Voc = []
    FF = []
    for data_y in all_data:
        Pmpp_x = [];Isc_x = [];Voc_x = [];FF_x = []
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
