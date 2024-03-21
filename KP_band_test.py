from solcore import si, material
from solcore.structure import Layer, Structure
from solcore.constants import *
from solcore.quantum_mechanics import schrodinger
import solcore.quantum_mechanics as QM
import numpy as np
import matplotlib.pyplot as plt
from solcore.quantum_mechanics.kp_bulk import kp_bands
from solcore.quantum_mechanics.structure_utilities import assemble_qw_structure, structure_to_potentials
from solcore.quantum_mechanics.heterostructure_alignment import VBO_align
from solcore.quantum_mechanics.strain import strain_calculation_parameters
from solcore.quantum_mechanics.kp_QW import solve_bandstructure_QW
from solcore.quantum_mechanics.potential_utilities import potentials_to_wavefunctions_energies
from test_QD_typeI_andtypeII.save_picture import schrodinger_graph_LDOS

#===============================================================
#setup
T = 300
wl = np.linspace(350, 1200, 401) * 1e-9

def printstructure(solar_cell):
    space = "+" +'='*70 + "+"
    print(space+ '\n' + f"\n".join(["{}".format(layer) for layer in solar_cell])+ '\n' + space)
    return str(space+ '\n' + f"\n".join(["{}".format(layer) for layer in solar_cell])+ '\n' + space)

def show_QD_graph(list_struc):
    # InSb_no_strain = material("InSb")(T=T)
    # struc = Structure( list_struc ,substrate = p_GaAs, T=T)
    RS, bands = QM.schrodinger(Structure(
        # [Layer(width=si("100 nm"), material=n_GaAs, role="Emitter")]+
        list_struc * 3
        # +[Layer(width=si("100 nm"), material=p_GaAs, role="Emitter"),]
        , substrate=i_GaAs, T=T)
        , quasiconfined=0.01
        , num_eigenvalues=20, show=False
        , mode='strain'
        )
    return RS, bands
def nkplot(Material,range_min_nm,range_max_nm,plot=False,):
    import matplotlib.pyplot as plt
    from solcore import siUnits as unit
    n = [Material.n(unit(i,'nm')) for i in range(range_min_nm, range_max_nm)]
    k = [Material.k(unit(i,'nm')) for i in range(range_min_nm, range_max_nm)]
    if plot is True:
        plt.plot(n, label=F'n_{Material}', color='red')
        plt.plot(k, label=F'k_{Material}', color='blue')
        plt.legend()
        plt.show()
    return n,k,[i for i in range(range_min_nm, range_max_nm)]

#===============================================================
#===============================================================
#material (ref : Electrical and optical properties of InSb/GaAg QDSC for photovoltaic)

n_GaAs = material('GaAs')(T=T, Nd=si('1e17 cm-3'), )
n_GaAs_min = material("GaAs")(T=T, Nd=si('5e16 cm-3'), )
n_AlInP = material("AlInP")(T=T, Al=0.42, Nd=si('3e16 cm-3'))

i_GaAs = material("GaAs")(T=T, strained=True, band_gap=si("1.422 eV"))
p_GaAs_min = material("GaAs")(T=T, Na=si('1e16 cm-3'), )
p_GaAs = material("GaAs")(T=T, Na=si("1e17 cm-3"), )
# print(si("4.59 eV"))
InSb = material("InSb")(T=T
                        , strained=True
                        , electron_mobility=7.7
                        , hole_mobility=0.0850,valence_band_offset=si("0.0 eV")
                        , band_gap=si("0.173723 eV"), spin_orbit_splitting=si("0.81 eV")
                        # , gamma1=34.8, gamma2=15.5, gamma3=16.5
                        # , a_c=si("-6.94"), a_v=si("-0.36 eV"), b=si("-2 eV")
                        )
# https://www.ioffe.ru/SVA/NSM/Semicond/InSb/basic.html (electron_affinity)
#https://www.ioffe.ru/SVA/NSM/Semicond/InSb/electric.html
#

# SR, bands = show_QD_graph(
#     [
#     # Layer(width=barrier, material=Bmat, role="barrier"),
#     Layer(width=si("5 nm"), material=i_GaAs, role="barrier"),
#     Layer(width=si("10 nm"), material=InSb,   role="well"), # 5-20 nm
#     Layer(width=si("5 nm"), material=i_GaAs, role="barrier"),
# ]
# )
# schrodinger_graph_LDOS(SR)
# plt.legend()
# plt.tight_layout()
# plt.show()
def get_structure_to_potentials():
    mode = {}
    GaAs = material("GaAs")(T=300)
    InSb = material("InSb")(T=300, strained=True
                            , electron_mobility=7.7
                            , hole_mobility=0.0850
                            ,valence_band_offset=si("0.0 eV")
                            )
    bands = kp_bands(InSb, InSb, kx=0, ky=0, kz=0, graph=False, fit_effective_mass=True, effective_mass_direction="L",
                     return_so=True)
    bands = kp_bands(GaAs, InSb, kx=0, ky=0, kz=0, graph=False, fit_effective_mass=True, effective_mass_direction="L",
                     return_so=True)
    bulk = GaAs
    QW = InSb
    top_layer = Layer(width=si("20nm"), material=bulk)
    well_layer = Layer(width=si("7.2nm"), material=QW)
    barrier_layer = Layer(width=si("5 nm"), material=bulk)
    bottom_layer = top_layer
    test_structure = assemble_qw_structure(
        repeats=3,
        well=well_layer,
        bulk_l_top=top_layer,
        bulk_l_bottom=bottom_layer,
        barrier=barrier_layer,
    )
    GaSb = material("GaSb")(T=T, strained=True,
                            electron_mobility=si("3e3 cm2"),
                            hole_mobility=si("1e3 cm2"),
                            )
    test_structure =[
        # Layer(width=si(f"100 nm"), material=AlGaAs, role="barrier"),
        Layer(width=si(f"{100} nm"), material=i_GaAs, role="interlayer"),
        Layer(width=si(f"{20} nm"), material=InSb, role="well"), # 5-20 nm
        Layer(width=si(f"{100} nm"), material=i_GaAs, role="interlayer"),
        Layer(width=si(f"{15} nm"), material=GaSb, role="well"),
        Layer(width=si(f"{50} nm"), material=i_GaAs, role="interlayer"),

        # Layer(width=si(f"100 nm"), material=AlGaAs, role="barrier")
        ]
    # test_structure.substrate = bulk
    test_structure = Structure(test_structure, substrate=bulk)
    RS, band = schrodinger(test_structure, show=False, graphtype="potentialsLDOS")
    schrodinger_graph_LDOS(RS)
    align_test_structure = VBO_align(test_structure)
    fig1, ax_band = plt.subplots(2, 2, figsize=(16.875, 12))

    result = structure_to_potentials(align_test_structure, mode='kp4x4')
    ax_band[0, 0].plot(result['x'] * 1e9, result['Ve'] / q, label="Ve")
    ax_band[0, 0].plot(result['x'] * 1e9, result['Vhh'] / q, label="Vhh")
    ax_band[0, 0].plot(result['x'] * 1e9, result['Vlh'] / q, label="Vlh")
    ax_band[0, 0].plot(result['x'] * 1e9, result['Vso'] / q, label="Vso")
    ax_band[0, 0].set_ylim(-1.5, 1.0)
    ax_band[0, 0].set_title("mode='kp4x4'")


    mode['kp4x4'] = result

    result = structure_to_potentials(align_test_structure, mode='kp6x6')
    ax_band[0, 1].plot(result['x'] * 1e9, result['Ve'] / q, label="Ve")
    ax_band[0, 1].plot(result['x'] * 1e9, result['Vhh'] / q, label="Vhh")
    ax_band[0, 1].plot(result['x'] * 1e9, result['Vlh'] / q, label="Vlh")
    ax_band[0, 1].plot(result['x'] * 1e9, result['Vso'] / q, label="Vso")
    ax_band[0, 1].set_ylim(-1.5, 1.0)
    ax_band[0, 1].set_title("mode='kp6x6'")
    mode['kp6x6'] = result


    result = structure_to_potentials(align_test_structure, mode='strain')
    ax_band[1, 0].plot(result['x'] * 1e9, result['Ve'] / q, label="Ve")
    ax_band[1, 0].plot(result['x'] * 1e9, result['Vhh'] / q, label="Vhh")
    ax_band[1, 0].plot(result['x'] * 1e9, result['Vlh'] / q, label="Vlh")
    ax_band[1, 0].plot(result['x'] * 1e9, result['Vso'] / q, label="Vso")
    ax_band[1, 0].set_ylim(-1.5, 1.0)
    ax_band[1, 0].set_title("mode='strain'")
    mode['strain'] = result



    result = structure_to_potentials(align_test_structure, mode='relaxed')
    ax_band[1, 1].plot(result['x'] * 1e9, result['Ve'] / q, label="Ve")
    ax_band[1, 1].plot(result['x'] * 1e9, result['Vhh'] / q, label="Vhh")
    ax_band[1, 1].plot(result['x'] * 1e9, result['Vlh'] / q, label="Vlh")
    ax_band[1, 1].plot(result['x'] * 1e9, result['Vso'] / q, label="Vso")
    ax_band[1, 1].set_ylim(-1.5, 1.0)
    ax_band[1, 1].set_title("mode='relaxed'")
    mode['relaxed'] = result
    # bands = potentials_to_wavefunctions_energies(structure=test_structure)

    fig1.suptitle("InSb/GaAs band diagram calculation ")
    plt.legend()
    # print(result)
    plt.show()
    return mode, test_structure
def yo():

    GaAs = material("GaAs")(T=300)
    InSb = material("InSb")(T=300, strained=True
                            , electron_mobility=7.7
                            , hole_mobility=0.0850
                            , valence_band_offset=si("0.0 eV")
                            )
    bulk = GaAs
    QW = InSb
    top_layer = Layer(width=si("20nm"), material=bulk)
    well_layer = Layer(width=si("7.2nm"), material=QW)
    barrier_layer = Layer(width=si("5 nm"), material=bulk)
    bottom_layer = top_layer
    strain_parameters = strain_calculation_parameters(bulk, QW, should_print=True, SO=True)
def try_to_plot_band(data, structure ):
    for mode, potentials in data.items():
        if mode in ['kp4x4', 'kp6x6']:
            bands = solve_bandstructure_QW(potentials)

            result_band_edge = {
                "x": bands['x'],
                "potentials": {key: potentials[key] for key in potentials.keys() if key[0] in "Vx"},
                "effective_masses": {key: potentials[key] for key in potentials.keys() if key[0] in "mx"},
                "wavefunctions": {key: bands[key][:, 0] for key in bands.keys() if 'psi' in key},
                "E": {key: bands[key][:, 0] for key in bands.keys() if key[0] in 'E'},
            }

        else:
            bands = potentials_to_wavefunctions_energies(structure=structure)

            result_band_edge = {
                "x": bands['x'],
                "potentials": {key: potentials[key] for key in potentials.keys() if key[0] in "Vx"},
                "effective_masses": {key: potentials[key] for key in potentials.keys() if key[0] in "mx"},
                "wavefunctions": {key: bands[key] for key in bands.keys() if 'psi' in key},
                "E": {key: np.array(bands[key]) for key in bands.keys() if key[0] in "E"},
            }

        schrodinger_graph_LDOS(result_band_edge)

# mode, test_structure = get_structure_to_potentials()
AlInP = material("AlInP")(T=T, Al=0.42, Nd=si('3e17 cm-3'))
AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True)
#
get_structure_to_potentials()
# i_GaAs = material("GaAs")(T=T)
# InSb = material("InSb")(T=T, strained=True)
# SR = Structure(
# [Layer(width=si("15 nm"), material=i_GaAs, role="barrier")
#      ]+[
#     Layer(width=si("15 nm"), material=AlInP, role="barrier"),
#     Layer(width=si("15 nm"), material=i_GaAs,   role="well"), # 5-20 nm
#     Layer(width=si("15 nm"), material=AlGaAs, role="barrier"),
#     ] + [
#     Layer(width=si("15 nm"), material=i_GaAs, role="barrier")
#     ], substrate=i_GaAs)
# modes = ['kp8x8_bulk', "strain", "relaxed"]
# buffer = []
# for mode in modes:
#     # result_band_edge, bands = schrodinger(SR, mode=mode, show=True, graphtype='potentialsLDOS')
#     result_band_edge, bands = schrodinger(SR, mode=mode,graphtype='potentialsLDOS', num_eigenvalues=200, show=True)
#     buffer.append(result_band_edge)
#     with open('test_kp.pkl', 'wb') as fin:
#         pickle.dump(buffer, fin)
#         print('dictionary saved successfully to file')
    # schrodinger_graph_LDOS(result_band_edge)
# with open('test_kp.pkl', "rb") as fp:
#     data = pickle.load(fp)
# for i in data:
#     for j, k in i.items():
#         print(j)
#         print(k)
# for i in data:
#     schrodinger_graph_LDOS(i)
# plt.show()

# try_to_plot_band(mode, test_structure)
# plt.show()
#

# test_structure =[
#         Layer(width=si(f"100 nm"), material=AlGaAs, role="barrier"),
#         Layer(width=si(f"{50} nm"), material=i_GaAs, role="interlayer"),
#         Layer(width=si(f"{1} nm"), material=InSb, role="well"), # 5-20 nm
#         Layer(width=si(f"{50} nm"), material=i_GaAs, role="interlayer"),
#         # Layer(width=si(f"{20} nm"), material=GaSb, role="well"),
#         # Layer(width=si(f"{50} nm"), material=i_GaAs, role="interlayer"),
#         Layer(width=si(f"100 nm"), material=AlGaAs, role="barrier")
#         ]
#     # test_structure.substrate = bulk
# test_structure = Structure(test_structure, substrate=i_GaAs)
# schrodinger(test_structure, show=True, graphtype="potentialsLDOS")