import tkinter as tk
from solcore.solar_cell_solver import solar_cell_solver
import time
# from lib_save_file import *
from lib_save_data import *
from material_of_InSb_GaSb import *
from material_and_layer_QD import *
from solcore.light_source import LightSource

# ========================================================================
# setup
# light
# wl = np.linspace(300, 3000, 700) * 1e-9
wl = np.linspace(350, 1200, 401) * 1e-9  # version1
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




vint = np.linspace(-3, 3, 600)
V = np.linspace(-1.5, 0, 300)  # np
# V = np.linspace(-3.5, 3.5, 300)
# V = np.linspace(0,3.5,300) # pn
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

def simulation1D_sun_constant(version, sim_mat, plot_note, note=''):
    set_of_data = []
    for size, cell in sim_mat.items():
        data_mode = dict(allI=[], Isc=[], Voc=[], FF=[], Pmpp=[], absorbed=[], mode=size, xsc=[], nsc=[], psc=[],
                         xeq=[], neq=[], peq=[], note=note, list_structure=[], x_axis=plot_note['x_axis'], x_axis_name=plot_note["x_axis_name"])
        data_mode['list_structure'].append(
            "start item ================================================================================")
        _ = [data_mode['list_structure'].append(str(i)) for i in cell]
        data_mode['list_structure'].append(
            "end item   ================================================================================")
        print(data_mode['mode'])
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

def simulation2D_sun_constant(version, sim_mat, plot_note, note=''):
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

def fix_simulation1D(version, sim_fix, plot_note, fix_condition, fix_data,  note=''):
    count = 0
    for size, cell in sim_fix.items():
        if size in fix_condition:
            data_mode = dict(allI=[], Isc=[], Voc=[], FF=[], Pmpp=[], absorbed=[], mode=size, xsc=[], nsc=[], psc=[],
                             xeq=[], neq=[], peq=[], note=note, list_structure=[], x_axis=plot_note['x_axis'],
                             x_axis_name=plot_note["x_axis_name"])
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
            try:
                solar_cell_solver(cell, "iv"
                                  , user_options={"light_source": light_source,
                                                  "wavelength": wl,
                                                  "optics_method": None,
                                                  "light_iv": True,
                                                  "mpp": True,
                                                  "voltages": V,
                                                  "internal_voltages": vint,
                                                  }, )
            except:
                print(f"{size} is not working")
                data_mode['size'] += 'not working'
            data_mode = defultsave(cell, data_mode, version, save=False)
            fix_data[count] = data_mode
            back_up_data(fix_data, version)
        count += 1
    return fix_data
# ========================================================================
# show
#
def sim0D(version, sim_mat, note):
    start = time.perf_counter()
    # version = "dot_InSb_default"
    # sim_mat = dot_InSb_default()
    # note = 'reference solar cell of compare differance between no dot and dot'
    data = simulation0D(version, sim_mat, note=note)
    stop = time.perf_counter()
    hours, minutes, seconds = sec_to_hms(stop - start)
    print(f"this run take time {hours}h/{minutes}min/{seconds}sec")
    # root = tk.Tk()
    # root.withdraw()
    # show_warning(f"this run take time {hours} hours/ {minutes} minutes/ {seconds} seconds")
    save_all_file_0d(data, version, con_light)
    # movefile(f'Carrier_distribution_{version}.html', f'{version}')

    # root.update()


def sim1D(version, sim_mat, note):
    start = time.perf_counter()
    # version = "dot_InSb_n_sweep"
    # sim_mat, plot_note = dot_InSb_n_sweep()
    # note = 'check between respond between n and dot'
    set_of_data = simulation1D(version, sim_mat, note=note)
    stop = time.perf_counter()
    hours, minutes, seconds = sec_to_hms(stop - start)
    print(f"this run take time {hours} hours/ {minutes} minutes/ {seconds} seconds")
    # root = tk.Tk()
    # root.withdraw()
    save_set_of_data(set_of_data, version, con_light)
    movefile(f'Carrier_distribution_{version}.html', f'{version}')

    # show_warning(f"this run take time {hours} hours/ {minutes} minutes/ {seconds} seconds")
    # root.update()


def sim1D_sun_constant(version, sim_mat, plot_note, note):  # sc = simulation at 1 sun
    start = time.perf_counter()
    # version = "dot_InSb_n_sweep"
    # sim_mat, plot_note = dot_InSb_n_sweep()
    # note = 'check between respond between n and dot'
    set_of_data_sun_constant = simulation1D_sun_constant(version, sim_mat, plot_note, note=note)
    stop = time.perf_counter()
    hours, minutes, seconds = sec_to_hms(stop - start)
    print(f"this run take time {hours} hours/ {minutes} minutes/ {seconds} seconds")
    # root = tk.Tk()
    # root.withdraw()
    save_set_of_data_sun_constant(set_of_data_sun_constant, version)
    # note_from_mat = dict(x_axis=list, x_axis_name="txt")
    movefile(f'Carrier_distribution_{version}.html', f'{version}')
    # show_warning(f"this run take time {hours} hours/ {minutes} minutes/ {seconds} seconds")
    # root.update()


def sim2D_sun_constant(version, sim_mat, plot_note, note):
    start = time.perf_counter()
    version = "InSb_dot_size_sc"
    sim_mat, plot_note = InSb_dot_size_sweep()
    note = 'insert InSb dot in GaAs ref that have verier dot size'
    set_of_data_sun_constant = simulation2D_sun_constant(version, sim_mat, plot_note, note=note)
    stop = time.perf_counter()
    hours, minutes, seconds = sec_to_hms(stop - start)
    print(f"this run take time {hours} hours/ {minutes} minutes/ {seconds} seconds")
    root = tk.Tk()
    root.withdraw()
    save_set_of_data_sun_constant(set_of_data_sun_constant, version)
    # note_from_mat = dict(x_axis=list, x_axis_name="txt")
    movefile(f'Carrier_distribution_{version}.html', f'{version}')
    show_warning(f"this run take time {hours} hours/ {minutes} minutes/ {seconds} seconds")
    # root.update()

def load(version, is1D=False, ):
    if is1D:
        set_of_data = load_old_data("QDSC_InSb_and_GaSb_barrier_mod.pkl")
        save_set_of_data(set_of_data, version, con_light)
        # movefile(f'Carrier_distribution_{version}.html', f'{version}')

    else:
        data = load_old_data('QDSC_InAs_GaSb_under_interlayer.pkl')
        save_all_file_0d(data, version, con_light)
        # movefile(f'Carrier_distribution_{version}.html', f'{version}')


def main():
    # set_of_data = load_old_data("QDSC_InSb_and_GaSb_barrier_mod.pkl")
    # version = "InSb_dot_size_sc"
    # set_of_data_sun_constant = load_old_data("InSb_dot_size_barrier_mod.pkl")
    # for i in set_of_data_sun_constant:
    #     print(i['Pmpp'])
    # save_set_of_data_sun_constant(set_of_data_sun_constant, version)
    # movefile(f'Carrier_distribution_{version}.html', f'{version}')
    # sim0D()
    # sim1D()
    # version = "dot_InSb_n_sweep"
    # sim_fix, plot_note = dot_InSb_n_sweep()
    # num = 0
    # replot_list = [1, 4, 5 ,7]
    # fix_condition = list()
    # for size, _ in sim_fix.items():
    #     if num in replot_list:
    #         fix_condition.append(size)
    #     num += 1
    # print(fix_condition)
    # fix_data = load_old_data('dot_InSb_n_sweep.pkl')
    # fix_simulation1D(version, sim_fix, plot_note, fix_condition, fix_data,  note='fix_data')
    start = time.perf_counter()
    #
    # version = "dot_InSb_default"
    # sim_mat= dot_InSb_default()
    # note = 'default data from solcore'
    # sim0D(version, sim_mat, note)
    #
    # version = "dot_InSb_reference"
    # sim_mat = dot_InSb_reference()
    # note = 'reference'
    # sim0D(version, sim_mat, note)
    #
    # version = "dot_InSb_n_top_sweep_sc"
    # sim_mat, plot_note = dot_InSb_n_top_sweep()
    # note = 'default'
    # sim1D_sun_constant(version, sim_mat, plot_note, note)
    # try:
    #     version = "dot_InSb_n_inter_sweep_sc"
    #     sim_mat, plot_note = dot_InSb_n_inter_sweep()
    #     note = 'default'
    #     sim1D_sun_constant(version, sim_mat, plot_note, note)
    # except:
    #     pass
    # try:
    #     version = "dot_InSb_n_bot_sweep_sc"
    #     sim_mat, plot_note = dot_InSb_n_bot_sweep()
    #     note = 'default'
    #     sim1D_sun_constant(version, sim_mat, plot_note, note)
    # except:
    #     pass

    version = "InSb_dot_size_sweep_sc"
    sim_mat, plot_note = InSb_dot_size_sweep()
    note = 'default'
    sim1D_sun_constant(version, sim_mat, plot_note, note)

    # set_of_data = load_old_data("InSb_dot_size_sweep_sc.pkl")
    # print(len(set_of_data))
    # sim0D(version,sim_mat,note)

    # load("QDSC_InSb_and_GaSb_barrier_mod", is1D=True)
    stop = time.perf_counter()
    hours, minutes, seconds = sec_to_hms(stop - start)
    print(f"this run take time {hours} hours/ {minutes} minutes/ {seconds} seconds")


if __name__ == "__main__":
    main()
    plt.show()


