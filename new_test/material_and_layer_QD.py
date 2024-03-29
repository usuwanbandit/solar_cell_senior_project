# import solcore
from solcore.material_data.mobility import calculate_AlGaAs, mobility_low_field, calculate_mobility
from solcore import si, material, asUnit
from solcore.structure import Layer, Structure, Junction, SolcoreMaterialToStr
from solcore.solar_cell import SolarCell
import solcore.quantum_mechanics as QM
import solcore.poisson_drift_diffusion as PDD
# from save_picture import schrodinger_graph_LDOS
import solcore.material_data
import matplotlib.pyplot as plt
# from solcore.quantum_mechanics.high_level_kp_QW import schrodinger
# from save_picture import schrodinger_graph_LDOS
# from new_version_saveing_date import wl
from constant import *
import numpy as np
# import matplotlib.pyplot as plt
# from solcore.quantum_mechanics.kp_bulk import KPbands
# import pickle

# ==================================================================================================================
# setup
# T = 300
# wl = np.linspace(350, 1200, 401) * 1e-9
# InSb Auger ref  The InSb Auger recombination coefficient derived
#  from the IR–FIR dynamical plasma reflectivity
def printstructure(solar_cell):
    space = "+" + '=' * 70 + "+"
    print(space + '\n' + f"\n".join(["{}".format(layer) for layer in solar_cell]) + '\n' + space)
    return str(space + '\n' + f"\n".join(["{}".format(layer) for layer in solar_cell]) + '\n' + space)

# def show_QD_graph(list_struc):
#     # InSb_no_strain = material("InSb")(T=T)
#     # struc = Structure( list_struc ,substrate = p_GaAs, T=T)
#     RS, bands = QM.schrodinger(Structure(
#         # [Layer(width=si("100 nm"), material=n_GaAs, role="Emitter")]+
#         list_struc * 3
#         # +[Layer(width=si("100 nm"), material=p_GaAs, role="Emitter"),]
#         , substrate=i_GaAs, T=T)
#         , quasiconfined=0.01
#         , num_eigenvalues=10
#         , show=False
#         # , graphtype='potentialsLDOS'
#         , mode='kp6x6'
#     )
#     return RS, bands

def nkplot(Material, range_min_nm, range_max_nm, plot=False, ):
    import matplotlib.pyplot as plt
    from solcore import siUnits as unit
    n = [Material.n(unit(i, 'nm')) for i in range(range_min_nm, range_max_nm)]
    k = [Material.k(unit(i, 'nm')) for i in range(range_min_nm, range_max_nm)]
    if plot is True:
        plt.plot(n, label=F'n_{Material}', color='red')
        plt.plot(k, label=F'k_{Material}', color='blue')
        plt.legend()
        plt.show()
    return n, k, [i for i in range(range_min_nm, range_max_nm)]

# n_GaAs = material('GaAs')(T=T, Nd=si('1e17 cm-3'), )
# i_GaAs = material("GaAs")(T=T)
# i_GaAs_barrier = material("GaAs")(T=T, strained=True, eff_mass_electron_Gamma=0.067
#                                   , eff_mass_hh_z=0.51
#                                   , eff_mass_lh_z=0.082)
# p_GaAs = material("GaAs")(T=T, Na=si("1e17 cm-3"), )
# InSb = material("InSb")(T=T
#                         , strained=True
#                         , electron_mobility=7.7
#                         , hole_mobility=0.0850, valence_band_offset=si("0.0 eV")
#                         , band_gap=si("0.173723 eV"), spin_orbit_splitting=si("0.81 eV")
#                         , gamma1=34.8, gamma2=15.5, gamma3=16.5
#                         , a_c=si("-6.94 eV"), a_v=si("-0.36 eV"), b=si("-2 eV")
#                         )
MgF2 = material("MgF2")(T=T)
ZnS = material("ZNSCUB", sopra=True)(T=T, )
# Layer(width=si("100 nm"), material=MgF2, role="AR1")
# Layer(width=si("50 nm"), material=ZnS, role="AR2")

#end setup
# ==================================================================================================================
# material (ref : Electrical and optical properties of InSb/GaAg QDSC for photovoltaic)

def ref_GaAs():
    n_doping = np.logspace(16, 19, 5)
    plot_note = dict(x_axis=n_doping, x_axis_name="n_doping (cm-3)")
    solar_each_size_1 = {}
    for i in n_doping:
        #define material
        n_GaAs = material('GaAs')(T=T, Nd=si(f'{i} cm-3'), )
        p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )

        GaAs_junction = Junction([
                                     Layer(width=si("600 nm"), material=n_GaAs, role="Emitter"),
                                 ]
                                 # +QW_list
                                 + [
                                     Layer(width=si("1700 nm"), material=p_GaAs, role="Emitter"),
                                 ],
                                 T=T, kind="PDD", )
        my_solar_cell = SolarCell([
            # Layer(width=si("100 nm"), material=MgF2, role="AR1"),
            # Layer(width=si("50 nm"), material=ZnS, role="AR2"),
            GaAs_junction,
        ]
            , T=T, substrate=p_GaAs)
        solar_each_size_1[f"n doping ={i:.2e} cm-3"] = my_solar_cell

    return solar_each_size_1, plot_note
def ref_GaAs_n_sweep():
    # define setup
    n_size = np.linspace(200, 1000, 9)
    # modes = ['kp8x8_bulk']
    print(n_size)
    plot_note = dict(x_axis=n_size, x_axis_name="Dot size(nm)")
    solar_each_size_1 = {}
    for size in n_size:
        # define material
        # AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True, Nd=si("1e17 cm-3"))
        n_GaAs = material('GaAs')(T=T, Nd=si('1e17 cm-3'), )
        p_GaAs = material("GaAs")(T=T, Na=si("1e17 cm-3"), )
        # =============================================================================================
        # combine material

        GaAs_junction = Junction([
                                     Layer(width=si(f"{size} nm"), material=n_GaAs, role="Emitter"),
                                     Layer(width=si("1700 nm"), material=p_GaAs, role="Emitter"),
                                 ],
                                 T=T, kind="PDD", substrate=p_GaAs)
        my_solar_cell = SolarCell([
            GaAs_junction,
        ]
            , T=T, substrate=p_GaAs)
        solar_each_size_1[f"n size ={size} nm"] = my_solar_cell
    return solar_each_size_1, plot_note
# ref_GaAs_n_sweep()
def dot_InSb_default():
    i_GaAs = material('GaAs')(T=T,  )
    #define material
    n_GaAs = material('GaAs')(T=T, Nd=si('1e18 cm-3'), )
    p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
    n_GaAs_barrier = material('GaAs')(T=T, Nd=si('1e17 cm-3'),strained=True )
    i_GaAs_barrier = material("GaAs")(T=T, strained=True)
    InSb1 = material("InSb")(T=T
                            , strained=True
                            , valence_band_offset=si("0.0 eV")
                            , band_gap=si("0.173723 eV")
                            , lattice_constant=6.4793e-10
                            , gamma1=34.8, gamma2=15.5, gamma3=16.6
                            , a_c=si("-6.93 eV"), a_v=si("-0.36 eV"), b=si("-2 eV"), d=si("-4.7 eV")
                            , c11=si("684.7 GPa"), c12=si("373.5 GPa"), c44=si("311.1 GPa")
                            , interband_matrix_element=si("23.3 eV")
                            , spin_orbit_splitting=si("0.81 eV")
                            , eff_mass_electron_Gamma=0.0135
                            , eff_mass_hh_z=0.43
                            , eff_mass_lh_z=0.015
                            , eff_mass_electron=0.014
                            , electron_mobility=si("78000 cm2")
                            , hole_mobility=si("850 cm2")
                            , electron_affinity=si("4.59 eV")
                            , electron_minority_lifetime=si("1e-6 s")
                            , hole_minority_lifetime=si("1e-9 s")
                            , relative_permittivity=13.943
                            , electron_auger_recombination=si("1e-42 cm6")
                            , hole_auger_recombination=si("1e-42 cm6")
                            )
    InSb = material("InSb")(T=T
                            , strained=True
                            , electron_mobility=7.8
                            , hole_mobility=0.0850, valence_band_offset=si("0.0 eV")
                            )
    # reference :https://www.ioffe.ru/SVA/NSM/Semicond/InSb/basic.html (electron_affinity)
    # reference :https://www.ioffe.ru/SVA/NSM/Semicond/InSb/electric.html
    #========================================================================================================
    #combine material
    QW = PDD.QWunit([
        Layer(width=si("100 nm"), material=i_GaAs_barrier, role="barrier"),
        Layer(width=si("1 nm"), material=InSb, role="well"),  # 5-20 nm
        Layer(width=si("100 nm"), material=n_GaAs_barrier, role="barrier"),
    ], T=T, repeat=1, substrate=i_GaAs, )
    QW_list = QW.GetEffectiveQW(wavelengths=wl)
    GaAs_junction = Junction([
                                 Layer(width=si("350 nm"), material=n_GaAs, role="Emitter"),
                             ]
                             +QW_list
                             + [
                                 Layer(width=si("200 nm"), material=n_GaAs, role="Emitter"),
                                 Layer(width=si("1700 nm"), material=p_GaAs, role="Emitter"),
                             ],
                             T=T, kind="PDD", )
    my_solar_cell = SolarCell([
        # Layer(width=si("100 nm"), material=MgF2, role="AR1"),
        # Layer(width=si("50 nm"), material=ZnS, role="AR2"),
        GaAs_junction,
    ]
        , T=T, substrate=p_GaAs)
    return my_solar_cell
def dot_InSb_reference():
    #define material
    i_GaAs = material('GaAs')(T=T,  )
    n_GaAs = material('GaAs')(T=T, Nd=si('1e18 cm-3'), )
    p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
    n_GaAs_barrier = material('GaAs')(T=T, Nd=si('1e17 cm-3'),strained=True )
    i_GaAs_barrier = material("GaAs")(T=T, strained=True)
    InSb1 = material("InSb")(T=T
                            , strained=True
                            , valence_band_offset=si("0.0 eV")
                            , band_gap=si("0.173723 eV")
                            , lattice_constant=6.4793e-10
                            , gamma1=34.8, gamma2=15.5, gamma3=16.6
                            , a_c=si("-6.93 eV"), a_v=si("-0.36 eV"), b=si("-2 eV"), d=si("-4.7 eV")
                            , c11=si("684.7 GPa"), c12=si("373.5 GPa"), c44=si("311.1 GPa")
                            , interband_matrix_element=si("23.3 eV")
                            , spin_orbit_splitting=si("0.81 eV")
                            , eff_mass_electron_Gamma=0.0135
                            , eff_mass_hh_z=0.43
                            , eff_mass_lh_z=0.015
                            , eff_mass_electron=0.014
                            , electron_mobility=si("78000 cm2")
                            , hole_mobility=si("850 cm2")
                            , electron_affinity=si("4.59 eV")
                            # , electron_minority_lifetime=si("1e-6 s")
                            # , hole_minority_lifetime=si("1e-9 s")
                            , relative_permittivity=13.943
                            , electron_auger_recombination=si("1e-42 cm6")
                            , hole_auger_recombination=si("1e-42 cm6")
                            )
    InSb = material("InSb")(T=T, strained=True)
    # reference :https://www.ioffe.ru/SVA/NSM/Semicond/InSb/basic.html (electron_affinity)
    # reference :https://www.ioffe.ru/SVA/NSM/Semicond/InSb/electric.html
    #========================================================================================================
    #combine material
    QW = PDD.QWunit([
        Layer(width=si("100 nm"), material=i_GaAs_barrier, role="barrier"),
        Layer(width=si("1 nm"), material=InSb1, role="well"),  # 5-20 nm
        Layer(width=si("100 nm"), material=n_GaAs_barrier, role="barrier"),
    ], T=T, repeat=1, substrate=i_GaAs, )
    QW_list = QW.GetEffectiveQW(wavelengths=wl)
    GaAs_junction = Junction([
                                 Layer(width=si("350 nm"), material=n_GaAs, role="Emitter"),
                             ]
                             +QW_list
                             + [
                                 Layer(width=si("250 nm"), material=n_GaAs, role="Emitter"),
                                 Layer(width=si("1700 nm"), material=p_GaAs, role="Emitter"),
                             ],
                             T=T, kind="PDD", )
    my_solar_cell = SolarCell([
        # Layer(width=si("100 nm"), material=MgF2, role="AR1"),
        # Layer(width=si("50 nm"), material=ZnS, role="AR2"),
        GaAs_junction,
    ]
        , T=T, substrate=p_GaAs)
    return my_solar_cell
def dot_InSb_n_bot_sweep():
    # define setup
    dot_size = np.linspace(10, 500, 100)
    # modes = ['kp8x8_bulk']
    print(dot_size)
    plot_note = dict(x_axis=dot_size, x_axis_name="n_Layer between dot and p(nm)")
    solar_each_size_1 = {}
    for dot in dot_size:
        # define material
        # AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True, Nd=si("1e17 cm-3"))
        n_GaAs = material('GaAs')(T=T, Nd=si('1e18 cm-3'), )
        i_GaAs = material("GaAs")(T=T)
        i_GaAs_barrier = material("GaAs")(T=T, strained=True, eff_mass_electron_Gamma=0.067
                                          , eff_mass_hh_z=0.51
                                          , eff_mass_lh_z=0.082)
        n_GaAs_barrier = material("GaAs")(T=T, strained=True, eff_mass_electron_Gamma=0.067
                                          , eff_mass_hh_z=0.51
                                          , eff_mass_lh_z=0.082, Nd=si('1e17 cm-3'))
        p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
        InSb = material("InSb", sopra=True)(T=T
                                             , strained=True
                                             , valence_band_offset=si("0.0 eV")
                                             , band_gap=si("0.173723 eV")
                                             , lattice_constant=6.4793e-10
                                             , gamma1=34.8, gamma2=15.5, gamma3=16.6
                                             , a_c=si("-6.93 eV"), a_v=si("-0.36 eV"), b=si("-2 eV"), d=si("-4.7 eV")
                                             , c11=si("684.7 GPa"), c12=si("373.5 GPa"), c44=si("311.1 GPa")
                                             , interband_matrix_element=si("23.3 eV")
                                             , spin_orbit_splitting=si("0.81 eV")
                                             , eff_mass_electron_Gamma=0.0135
                                             , eff_mass_hh_z=0.05823949620355507
                                             , eff_mass_lh_z=0.0033633751606916276
                                             , eff_mass_electron=0.0022617432780656557
                                             , electron_mobility=si("78000 cm2")
                                             , hole_mobility=si("500 cm2")
                                             , electron_affinity=si("4.59 eV")
                                             , electron_minority_lifetime=si("1e-6 s")
                                             , hole_minority_lifetime=si("1e-8 s")
                                             , relative_permittivity=13.943
                                             , electron_auger_recombination=si("1e-42 cm6")
                                             , hole_auger_recombination=si("1e-42 cm6")
                                             )
        GaSb = material("GaSb")(T=T, strained=True, )
        # =============================================================================================
        # combine material
        QW = PDD.QWunit([
            # Layer(width=si(f"15 nm"), material=AlGaAs, role="barrier"),
            Layer(width=si("100 nm"), material=i_GaAs_barrier, role="barrier"),
            Layer(width=si(f"1 nm"), material=InSb, role="well"),  # 5-20 nm
            Layer(width=si("100 nm"), material=n_GaAs_barrier, role="barrier"),
            # Layer(width=si(f"15 nm"), material=AlGaAs, role="barrier")
        ], T=T, repeat=1, substrate=i_GaAs)
        QW_list = QW.GetEffectiveQW(wavelengths=wl, use_Adachi=True, blur=True, blurmode="left", periodic=False, filter_strength=si('0.01 eV'))
        GaAs_junction = Junction([
                                     Layer(width=si("350 nm"), material=n_GaAs, role="Emitter"),
                                 ]
                                 + QW_list
                                 + [
                                     Layer(width=si(f"{dot} nm"), material=n_GaAs, role="Emitter"),
                                     Layer(width=si("1700 nm"), material=p_GaAs, role="Emitter"),
                                 ],
                                 T=T, kind="PDD", substrate=p_GaAs)
        my_solar_cell = SolarCell([
            GaAs_junction,
        ]
            , T=T, substrate=p_GaAs)
        solar_each_size_1[f"n layer = {dot:.2e}nm"] = my_solar_cell
    return solar_each_size_1, plot_note
def dot_InSb_n_top_sweep():
    # define setup
    dot_size = np.linspace(10, 500, 10)
    # modes = ['kp8x8_bulk']
    print(dot_size)
    plot_note = dict(x_axis=dot_size, x_axis_name="top layer (nm)")
    solar_each_size_1 = {}
    for dot in dot_size:
        # define material
        # AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True, Nd=si("1e17 cm-3"))
        n_GaAs = material('GaAs')(T=T, Nd=si('1e18 cm-3'), )
        i_GaAs = material("GaAs")(T=T)
        i_GaAs_barrier = material("GaAs")(T=T, strained=True, eff_mass_electron_Gamma=0.067
                                          , eff_mass_hh_z=0.51
                                          , eff_mass_lh_z=0.082)
        n_GaAs_barrier = material("GaAs")(T=T, strained=True, eff_mass_electron_Gamma=0.067
                                          , eff_mass_hh_z=0.51
                                          , eff_mass_lh_z=0.082, Nd=si('1e17 cm-3'))
        p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
        InSb = material("InSb", sopra=True)(T=T
                                             , strained=True
                                             , valence_band_offset=si("0.0 eV")
                                             , band_gap=si("0.173723 eV")
                                             , lattice_constant=6.4793e-10
                                             , gamma1=34.8, gamma2=15.5, gamma3=16.6
                                             , a_c=si("-6.93 eV"), a_v=si("-0.36 eV"), b=si("-2 eV"), d=si("-4.7 eV")
                                             , c11=si("684.7 GPa"), c12=si("373.5 GPa"), c44=si("311.1 GPa")
                                             , interband_matrix_element=si("23.3 eV")
                                             , spin_orbit_splitting=si("0.81 eV")
                                             , eff_mass_electron_Gamma=0.0135
                                             , eff_mass_hh_z=0.05823949620355507
                                             , eff_mass_lh_z=0.0033633751606916276
                                             , eff_mass_electron=0.0022617432780656557
                                             , electron_mobility=si("78000 cm2")
                                             , hole_mobility=si("500 cm2")
                                             , electron_affinity=si("4.59 eV")
                                             , electron_minority_lifetime=si("1e-6 s")
                                             , hole_minority_lifetime=si("1e-8 s")
                                             , relative_permittivity=13.943
                                             , electron_auger_recombination=si("1e-42 cm6")
                                             , hole_auger_recombination=si("1e-42 cm6")
                                             )

        GaSb = material("GaSb")(T=T, strained=True, )
        # =============================================================================================
        # combine material
        QW = PDD.QWunit([
            # Layer(width=si(f"15 nm"), material=AlGaAs, role="barrier"),
            Layer(width=si("100 nm"), material=i_GaAs_barrier, role="barrier"),
            Layer(width=si(f"1 nm"), material=InSb, role="well"),  # 5-20 nm
            Layer(width=si("100 nm"), material=n_GaAs_barrier, role="barrier"),
            # Layer(width=si(f"15 nm"), material=AlGaAs, role="barrier")
        ], T=T, repeat=1, substrate=i_GaAs)
        QW_list = QW.GetEffectiveQW(wavelengths=wl, use_Adachi=True, blur=True, blurmode="left", periodic=False, filter_strength=si('0.01 eV'))
        GaAs_junction = Junction([
                                     Layer(width=si(f"{dot} nm"), material=n_GaAs, role="Emitter"),
                                 ]
                                 + QW_list
                                 + [
                                     Layer(width=si(f"200 nm"), material=n_GaAs, role="Emitter"),
                                     Layer(width=si("1700 nm"), material=p_GaAs, role="Emitter"),
                                 ],
                                 T=T, kind="PDD", substrate=p_GaAs)
        my_solar_cell = SolarCell([
            GaAs_junction,
        ]
            , T=T, substrate=p_GaAs)
        solar_each_size_1[f"n layer = {dot:.2e}nm"] = my_solar_cell
    return solar_each_size_1, plot_note

def dot_InSb_n_inter_sweep():
    # define setup
    dot_size = np.linspace(20, 300, 100)
    # modes = ['kp8x8_bulk']
    print(dot_size)
    plot_note = dict(x_axis=dot_size, x_axis_name="inter layer (nm)")
    solar_each_size_1 = {}
    for dot in dot_size:
        print(dot)
        # define material
        # AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True, Nd=si("1e17 cm-3"))
        n_GaAs = material('GaAs')(T=T, Nd=si('1e18 cm-3'), )
        i_GaAs = material("GaAs")(T=T)
        i_GaAs_barrier = material("GaAs")(T=T, strained=True, eff_mass_electron_Gamma=0.067
                                          , eff_mass_hh_z=0.51
                                          , eff_mass_lh_z=0.082)
        n_GaAs_barrier = material("GaAs")(T=T, strained=True, eff_mass_electron_Gamma=0.067
                                          , eff_mass_hh_z=0.51
                                          , eff_mass_lh_z=0.082, Nd=si('1e17 cm-3'))
        p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
        InSb = material("InSb", sopra=True)(T=T
                                             , strained=True
                                             , valence_band_offset=si("0.0 eV")
                                             , band_gap=si("0.173723 eV")
                                             , lattice_constant=6.4793e-10
                                             , gamma1=34.8, gamma2=15.5, gamma3=16.6
                                             , a_c=si("-6.93 eV"), a_v=si("-0.36 eV"), b=si("-2 eV"), d=si("-4.7 eV")
                                             , c11=si("684.7 GPa"), c12=si("373.5 GPa"), c44=si("311.1 GPa")
                                             , interband_matrix_element=si("23.3 eV")
                                             , spin_orbit_splitting=si("0.81 eV")
                                             , eff_mass_electron_Gamma=0.0135
                                             , eff_mass_hh_z=0.05823949620355507
                                             , eff_mass_lh_z=0.0033633751606916276
                                             , eff_mass_electron=0.0022617432780656557
                                             , electron_mobility=si("78000 cm2")
                                             , hole_mobility=si("500 cm2")
                                             , electron_affinity=si("4.59 eV")
                                             , electron_minority_lifetime=si("1e-6 s")
                                             , hole_minority_lifetime=si("1e-8 s")
                                             , relative_permittivity=13.943
                                             , electron_auger_recombination=si("1e-42 cm6")
                                             , hole_auger_recombination=si("1e-42 cm6")
                                             )
        GaSb = material("GaSb")(T=T, strained=True, )
        # =============================================================================================
        # combine material
        QW = PDD.QWunit([
            # Layer(width=si(f"15 nm"), material=AlGaAs, role="barrier"),
            Layer(width=si(f"{dot} nm"), material=i_GaAs_barrier, role="barrier"),
            Layer(width=si(f"1 nm"), material=InSb, role="well"),  # 5-20 nm
            Layer(width=si(f"{dot} nm"), material=n_GaAs_barrier, role="barrier"),
            # Layer(width=si(f"15 nm"), material=AlGaAs, role="barrier")
        ], T=T, repeat=1, substrate=i_GaAs)
        QW_list = QW.GetEffectiveQW(wavelengths=wl, use_Adachi=True, blur=True, blurmode="left", periodic=False, filter_strength=si('0.01 eV'))
        GaAs_junction = Junction([
                                     Layer(width=si("350 nm"), material=n_GaAs, role="Emitter"),
                                 ]
                                 + QW_list
                                 + [
                                     Layer(width=si(f"200 nm"), material=n_GaAs, role="Emitter"),
                                     Layer(width=si("1700 nm"), material=p_GaAs, role="Emitter"),
                                 ],
                                 T=T, kind="PDD", substrate=p_GaAs)
        my_solar_cell = SolarCell([
            GaAs_junction,
        ]
            , T=T, substrate=p_GaAs)
        solar_each_size_1[f"n layer = {dot:.2e}nm"] = my_solar_cell
    return solar_each_size_1, plot_note
# dot_InSb_n_inter_sweep()
def InSb_dot_size_sweep():
    # define setup
    dot_size = np.linspace(1, 3, 5)
    # modes = ['kp8x8_bulk']
    print(dot_size)
    plot_note = dict(x_axis=dot_size, x_axis_name="Dot size(nm)")
    solar_each_size_1 = {}
    for dot in dot_size:
        # define material
        AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True,
                                    # Nd=si("1e16 cm-3")
                                    )
        n_GaAs_plus = material('GaAs')(T=T, Nd=si('1e18 cm-3'), band_gap=si("1.422 eV"))

        n_GaAs = material('GaAs')(T=T, Nd=si('1e18 cm-3'), band_gap=si("1.422 eV"))
        p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
        i_GaAs = material("GaAs")(T=T, band_gap=si("1.422 eV"))
        i_GaAs_barrier = material("GaAs")(T=T
                                          , strained=True
                                          # , eff_mass_electron_Gamma=0.067
                                          # , eff_mass_hh_z=0.51
                                          # , eff_mass_lh_z=0.082
                                          # , band_gap=si("1.422 eV")
                                          )
        n_GaAs_barrier = material("GaAs")(T=T, strained=True, Nd=si("1e16 cm-3"))
        p_GaAs_barrier = material("GaAs")(T=T, strained=True, Na=si("1e16 cm-3"))

        InSb = material("InAsSb")(T=T
                                , strained=True
                                # , electron_mobility = calculate_mobility(material("Insb"),0, 0,0,T)
                                # , electron_mobility=7.8
                                # , hole_mobility=0.0850
                                # ,valence_band_offset=si("0.0 eV")
                                # , band_gap=si("0.173723 eV")
                                # , spin_orbit_splitting=si("0.81 eV")
                                # , relative_permittivity=13.943
                                )
        InSb1 = material("InSb", sopra=True)(T=T
                                 , strained=True
                                 , valence_band_offset=si("0.0 eV")
                                 , band_gap=si("0.173723 eV")
                                 , lattice_constant=6.4793e-10
                                 , gamma1=34.8, gamma2=15.5, gamma3=16.6
                                 , a_c=si("-6.93 eV"), a_v=si("-0.36 eV"), b=si("-2 eV"), d=si("-4.7 eV")
                                 , c11=si("684.7 GPa"), c12=si("373.5 GPa"), c44=si("311.1 GPa")
                                 , interband_matrix_element=si("23.3 eV")
                                 , spin_orbit_splitting=si("0.81 eV")
                                 , eff_mass_electron_Gamma=0.0135
                                 , eff_mass_hh_z= 0.05823949620355507
                                 , eff_mass_lh_z= 0.0033633751606916276
                                 , eff_mass_electron= 0.0022617432780656557
                                 , electron_mobility=si("78000 cm2")
                                 , hole_mobility=si("500 cm2")
                                 , electron_affinity=si("4.59 eV")
                                 , electron_minority_lifetime=si("1e-6 s")
                                 , hole_minority_lifetime=si("1e-8 s")
                                 , relative_permittivity=13.943
                                 , electron_auger_recombination=si("1e-42 cm6")
                                 , hole_auger_recombination=si("1e-42 cm6")
                                 )
        # InSb2 = material("InAsSb")(T=T
        #                          , Sb=0.5
        #                          , strained=True
        #                          , valence_band_offset=si("0.0 eV")
        #                          , band_gap=si("0.173723 eV")
        #                          , lattice_constant=6.4793e-10
        #                          , gamma1=34.8, gamma2=15.5, gamma3=16.6
        #                          , a_c=si("-6.93 eV"), a_v=si("-0.36 eV"), b=si("-2 eV"), d=si("-4.7 eV")
        #                          , c11=si("684.7 GPa"), c12=si("373.5 GPa"), c44=si("311.1 GPa")
        #                          , interband_matrix_element=si("23.3 eV")
        #                          , spin_orbit_splitting=si("0.81 eV")
        #                          , eff_mass_electron_Gamma=0.0135
        #                          , eff_mass_hh_z=0.05823949620355507
        #                          , eff_mass_lh_z=0.0033633751606916276
        #                          , eff_mass_electron=0.0022617432780656557
        #                          , electron_mobility=si("78000 cm2")
        #                          , hole_mobility=si("500 cm2")
        #                          , electron_affinity=si("4.59 eV")
        #                          , electron_minority_lifetime=si("1e-6 s")
        #                          , hole_minority_lifetime=si("1e-8 s")
        #                          , relative_permittivity=13.943
        #                          , electron_auger_recombination=si("1e-42 cm6")
        #                          , hole_auger_recombination=si("1e-42 cm6")
        #                          )
        GaSb = material("GaSb")(T=T, strained=True, )
        # =============================================================================================
        # combine material

        QW = PDD.QWunit([
            # Layer(width=si(f"50 nm"), material=AlGaAs, role="barrier"),
            Layer(width=si(f"25 nm"), material=i_GaAs, role="interlayer"),
            # Layer(width=si(f"1 nm"), material=InSb2, role="interlayer"),  # 5-20 nm
            Layer(width=si(f"{dot} nm"), material=InSb1, role="well"),  # 5-20 nm
            # Layer(width=si(f"1 nm"), material=InSb2, role="interlayer"),  # 5-20 nm
            Layer(width=si(f"25 nm"), material=i_GaAs, role="interlayer"),
            # Layer(width=si(f"50 nm"), material=AlGaAs, role="barrier")
        ], T=T, repeat=5, substrate=i_GaAs)
        E = 1240 / (wl * 1e9) * q
        alpha_params = {
            "well_width": QW.QW_width,
            "theta": 0,
            "eps": 13.943 * vacuum_permittivity,
            "espace": E,
            "hwhm": si("6meV"),
            "dimensionality": 0.2,
            "line_shape": "Gauss"
        }
        QW_list = QW.GetEffectiveQW(wavelengths=wl,
                                    use_Adachi=True,
                                    # blur=True,
                                    # blurmode="even",
                                    # periodic=False,
                                    # filter_strength=si('0.001 eV')
                                    alpha_params=alpha_params,
                                    )

        GaAs_junction = Junction([
                                     Layer(width=si("330 nm"), material=n_GaAs, role="Emitter"),
                                     Layer(width=si("100 nm"), material=i_GaAs, role="collector"),

                                 ]
                                 + QW_list
                                 + [
                                     Layer(width=si("100 nm"), material=i_GaAs, role="collector"),
                                     Layer(width=si("1700 nm"), material=p_GaAs, role="collector"),
                                 ],
                                 T=T, kind="PDD", substrate=p_GaAs
                                 ,sn=0, sp=0,)
        my_solar_cell = SolarCell([
            # Layer(width=si("100 nm"), material=MgF2, role="AR1"),
            # Layer(width=si("50 nm"), material=ZnS, role="AR2"),
            # Layer(width=si("230 nm"), material=n_GaAs_plus, role="Emitter"),
            GaAs_junction,
        ]
            , T=T, substrate=p_GaAs,  R_series=0)
        # for i in my_solar_cell.__dict__:
        #     print(i)
        solar_each_size_1[f"dot size ={dot:.2e} nm"] = my_solar_cell

    return solar_each_size_1, plot_note

def InSb_dot_layer_sweep():
    # define setup
    dot_size = np.array([10, 20, 30])
    # modes = ['kp8x8_bulk']
    print(dot_size)
    plot_note = dict(x_axis=dot_size, x_axis_name="QDs layer")
    solar_each_size_1 = {}
    for dot in dot_size:
        # define material
        n_GaAs = material('GaAs')(T=T, Nd=si('1e18 cm-3'))
        p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
        i_GaAs = material("GaAs")(T=T)
        i_GaAs_barrier = material("GaAs")(T=T
                                          , strained=True
                                          # , eff_mass_electron_Gamma=0.067
                                          # , eff_mass_hh_z=0.51
                                          # , eff_mass_lh_z=0.082
                                          # , band_gap=si("1.422 eV")
                                          )
        InSb = material("InSb", sopra=True)(T=T
                                            , strained=True
                                            , valence_band_offset=si("0.0 eV")
                                            , band_gap=si("0.173723 eV")
                                            , lattice_constant=6.4793e-10
                                            , gamma1=34.8, gamma2=15.5, gamma3=16.6
                                            , a_c=si("-6.93 eV"), a_v=si("-0.36 eV"), b=si("-2 eV"), d=si("-4.7 eV")
                                            , c11=si("684.7 GPa"), c12=si("373.5 GPa"), c44=si("311.1 GPa")
                                            , interband_matrix_element=si("23.3 eV")
                                            , spin_orbit_splitting=si("0.81 eV")
                                            , eff_mass_electron_Gamma=0.0135
                                            , eff_mass_hh_z=0.05823949620355507
                                            , eff_mass_lh_z=0.0033633751606916276
                                            , eff_mass_electron=0.0022617432780656557
                                            , electron_mobility=si("78000 cm2")
                                            , hole_mobility=si("500 cm2")
                                            , electron_affinity=si("4.59 eV")
                                            , electron_minority_lifetime=si("1e-6 s")
                                            , hole_minority_lifetime=si("1e-8 s")
                                            , relative_permittivity=13.943
                                            , electron_auger_recombination=si("1e-42 cm6")
                                            , hole_auger_recombination=si("1e-42 cm6")
                                            )
        # InSb2 = material("InAsSb")(T=T
        #                          , Sb=0.5
        #                          , strained=True
        #                          , valence_band_offset=si("0.0 eV")
        #                          , band_gap=si("0.173723 eV")
        #                          , lattice_constant=6.4793e-10
        #                          , gamma1=34.8, gamma2=15.5, gamma3=16.6
        #                          , a_c=si("-6.93 eV"), a_v=si("-0.36 eV"), b=si("-2 eV"), d=si("-4.7 eV")
        #                          , c11=si("684.7 GPa"), c12=si("373.5 GPa"), c44=si("311.1 GPa")
        #                          , interband_matrix_element=si("23.3 eV")
        #                          , spin_orbit_splitting=si("0.81 eV")
        #                          , eff_mass_electron_Gamma=0.0135
        #                          , eff_mass_hh_z=0.05823949620355507
        #                          , eff_mass_lh_z=0.0033633751606916276
        #                          , eff_mass_electron=0.0022617432780656557
        #                          , electron_mobility=si("78000 cm2")
        #                          , hole_mobility=si("500 cm2")
        #                          , electron_affinity=si("4.59 eV")
        #                          , electron_minority_lifetime=si("1e-6 s")
        #                          , hole_minority_lifetime=si("1e-8 s")
        #                          , relative_permittivity=13.943
        #                          , electron_auger_recombination=si("1e-42 cm6")
        #                          , hole_auger_recombination=si("1e-42 cm6")
        #                          )
        GaSb = material("GaSb")(T=T, strained=True, )
        # =============================================================================================
        # combine material

        QW = PDD.QWunit([
            # Layer(width=si(f"50 nm"), material=AlGaAs, role="barrier"),
            Layer(width=si(f"100 nm"), material=i_GaAs_barrier, role="interlayer"),
            # Layer(width=si(f"1 nm"), material=InSb2, role="interlayer"),  # 5-20 nm
            Layer(width=si(f"10 nm"), material=InSb, role="well"),  # 5-20 nm
            # Layer(width=si(f"1 nm"), material=InSb2, role="interlayer"),  # 5-20 nm
            Layer(width=si(f"100 nm"), material=i_GaAs_barrier, role="interlayer"),
            # Layer(width=si(f"50 nm"), material=AlGaAs, role="barrier")
        ], T=T, repeat=dot, substrate=i_GaAs)
        # E = 1240 / (wl * 1e9) * q
        # alpha_params = {
        #     "well_width": QW.QW_width,
        #     "theta": 0,
        #     "eps": 13.943 * vacuum_permittivity,
        #     "espace": E,
        #     "hwhm": si("6meV"),
        #     "dimensionality": 0.2,
        #     "line_shape": "Gauss"
        # }
        QW_list = QW.GetEffectiveQW(wavelengths=wl,
                                    use_Adachi=True,
                                    # blur=True,
                                    # blurmode="even",
                                    # periodic=False,
                                    # filter_strength=si('0.001 eV')
                                    # alpha_params=alpha_params,
                                    )

        GaAs_junction = Junction([
                                     Layer(width=si("200 nm"), material=n_GaAs, role="Emitter"),
                                     Layer(width=si("150 nm"), material=i_GaAs, role="collector"),

                                 ]
                                 + QW_list
                                 + [
                                     Layer(width=si("150 nm"), material=i_GaAs, role="collector"),
                                     Layer(width=si("1700 nm"), material=p_GaAs, role="collector"),
                                 ],
                                 T=T, kind="PDD", substrate=p_GaAs
                                 )
        my_solar_cell = SolarCell([
            # Layer(width=si("100 nm"), material=MgF2, role="AR1"),
            # Layer(width=si("50 nm"), material=ZnS, role="AR2"),
            # Layer(width=si("230 nm"), material=n_GaAs_plus, role="Emitter"),
            GaAs_junction,
        ]
            , T=T, substrate=p_GaAs,  R_series=0)
        # for i in my_solar_cell.__dict__:
        #     print(i)
        solar_each_size_1[f"dot stack = {dot}"] = my_solar_cell

    return solar_each_size_1, plot_note

# InSb_dot_size_sweep()


#===========================================================================================================
def InSb_dot_size_barrier_mod():
    # define setup
    dot_size = np.linspace(0.1, 3, 10)
    # modes = ['kp8x8_bulk']
    print(dot_size)
    plot_note = dict(x_axis=dot_size, x_axis_name="Dot size(nm)")
    solar_each_size_1 = {}
    for dot in dot_size:
        # define material
        AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True, Nd=si("1e16 cm-3"))
        n_GaAs = material('GaAs')(T=T, Nd=si('1e16 cm-3'), )
        i_GaAs = material("GaAs")(T=T)
        i_GaAs_barrier = material("GaAs")(T=T, strained=True, eff_mass_electron_Gamma=0.067
                                          , eff_mass_hh_z=0.51
                                          , eff_mass_lh_z=0.082)
        p_GaAs = material("GaAs")(T=T, Na=si("1e18 cm-3"), )
        InSb = material("InSb", sopra=True)(T=T
                                             , strained=True
                                             , valence_band_offset=si("0.0 eV")
                                             , band_gap=si("0.173723 eV")
                                             , lattice_constant=6.4793e-10
                                             , gamma1=34.8, gamma2=15.5, gamma3=16.6
                                             , a_c=si("-6.93 eV"), a_v=si("-0.36 eV"), b=si("-2 eV"), d=si("-4.7 eV")
                                             , c11=si("684.7 GPa"), c12=si("373.5 GPa"), c44=si("311.1 GPa")
                                             , interband_matrix_element=si("23.3 eV")
                                             , spin_orbit_splitting=si("0.81 eV")
                                             , eff_mass_electron_Gamma=0.0135
                                             , eff_mass_hh_z=0.05823949620355507
                                             , eff_mass_lh_z=0.0033633751606916276
                                             , eff_mass_electron=0.0022617432780656557
                                             , electron_mobility=si("78000 cm2")
                                             , hole_mobility=si("500 cm2")
                                             , electron_affinity=si("4.59 eV")
                                             , electron_minority_lifetime=si("1e-6 s")
                                             , hole_minority_lifetime=si("1e-8 s")
                                             , relative_permittivity=13.943
                                             , electron_auger_recombination=si("1e-42 cm6")
                                             , hole_auger_recombination=si("1e-42 cm6")
                                             )
        GaSb = material("GaSb")(T=T, strained=True, )
        # =============================================================================================
        # combine material
        QW = PDD.QWunit([
            Layer(width=si(f"10 nm"), material=AlGaAs, role="barrier"),
            Layer(width=si("5 nm"), material=i_GaAs_barrier, role="barrier"),
            Layer(width=si(f"{dot} nm"), material=InSb, role="well"),  # 5-20 nm
            Layer(width=si("5 nm"), material=i_GaAs_barrier, role="barrier"),
            Layer(width=si(f"10 nm"), material=AlGaAs, role="barrier")
        ], T=T, repeat=5, substrate=i_GaAs)
        QW_list = QW.GetEffectiveQW(wavelengths=wl, use_Adachi=True)
        GaAs_junction = Junction([
                                     Layer(width=si("50 nm"), material=n_GaAs, role="Emitter"),
                                 ]
                                 + QW_list
                                 + [
                                     Layer(width=si("100 nm"), material=n_GaAs, role="Emitter"),
                                     Layer(width=si("1700 nm"), material=p_GaAs, role="Collector"),
                                 ],
                                 T=T, kind="PDD", substrate=p_GaAs)
        my_solar_cell = SolarCell([
            GaAs_junction,
        ]
            , T=T, substrate=p_GaAs)
        solar_each_size_1[f"dot size ={dot} nm"] = my_solar_cell
    return solar_each_size_1, plot_note

# InSb_dot_size()
def QDSC_GaSb_Sw_dotsize():
    #define setup
    dot_size = [5, 10, 15, 20]
    # modes = ['kp8x8_bulk']
    print(dot_size)
    plot_note = dict(x_axis=dot_size, x_axis_name="Dot size(nm)")
    solar_each_size_1 = {}
    for dot in dot_size:
        #define material
        AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True)
        n_GaAs = material('GaAs')(T=T, Nd=si('1e16 cm-3'), band_gap=si("1.422 eV"))
        p_GaAs = material("GaAs")(T=T, Na=si("1e18 cm-3"), )
        i_GaAs = material("GaAs")(T=T, valence_band_offset= si('-0.59 eV'))
        i_GaAs_barrier = material("GaAs")(T=T, strained=True, eff_mass_electron_Gamma=0.067
                                          , eff_mass_hh_z=0.51
                                          , eff_mass_lh_z=0.082
                                          , valence_band_offset= si('-0.59 eV')
                                          )
        InSb = material("InSb")(T=T
                                , strained=True
                                , electron_mobility=7.7
                                , hole_mobility=0.0850, valence_band_offset=si("0.0 eV")
                                , band_gap=si("0.173723 eV"), spin_orbit_splitting=si("0.81 eV")
                                , gamma1=34.8, gamma2=15.5, gamma3=16.5
                                , a_c=si("-6.94 eV"), a_v=si("-0.36 eV"), b=si("-2 eV")
                                )
        GaSb = material("GaSb")(T=T, strained=True, hole_mobility=0.09, electron_mobility=0.48)
        #Carrier Mobility in GaSb–V2Ga5and GaSb–GaV3Sb5 Eutectic Alloys
        #=============================================================================================
        #combine material
        QW = PDD.QWunit([
            # Layer(width=si(f"15 nm"), material=AlGaAs, role="barrier"),
            Layer(width=si("20 nm"), material=i_GaAs, role="interlayer"),
            Layer(width=si(f"{dot} nm"), material=GaSb, role="well"),  # 5-20 nm
            Layer(width=si("20 nm"), material=i_GaAs, role="interlayer"),
            # Layer(width=si(f"15 nm"), material=AlGaAs, role="barrier")
        ], T=T, repeat=3, substrate=i_GaAs)
        QW_list = QW.GetEffectiveQW(wavelengths=wl, use_Adachi=True)
        GaAs_junction = Junction([
                                     Layer(width=si("230 nm"), material=n_GaAs, role="Emitter"),
                                 ]
                                 + QW_list
                                 + QW_list
                                 + [
                                     # Layer(width=si("330 nm"), material=n_GaAs, role="Emitter"),
                                     Layer(width=si("1700 nm"), material=p_GaAs, role="Collector"),
                                 ],
                                 T=T, kind="PDD", substrate=p_GaAs)
        my_solar_cell = SolarCell([
            GaAs_junction,
        ]
            , T=T, substrate=p_GaAs)
        solar_each_size_1[f"GaSb size ={dot:.2e} nm"] = my_solar_cell
    return solar_each_size_1, plot_note

def QDSC_GaSb_Sw_dotsize_ref():
    #define setup
    # Temperature Dependence of Carrier Extraction Processes in
    #  GaSb/AlGaAs Quantum Nanostructure Intermediate-Band
    #  Solar Cells
    dot_size = np.linspace(1, 10, 10)
    # modes = ['kp8x8_bulk']
    print(dot_size)
    plot_note = dict(x_axis=dot_size, x_axis_name="Dot size(nm)")
    solar_each_size_1 = {}
    for dot in dot_size:
        #define material
        AlGaAs_stain = material("AlGaAs")(T=T, Al=0.2, strained=True)
        p_AlGaAs_window = material("AlGaAs")(T=T, Al=0.8, Na=si("2e18 cm-3"))
        p_AlGaAs_enitter = material("AlGaAs")(T=T, Al=0.2, Na=si("1e18 cm-3"))
        n_AlGaAs_base = material("AlGaAs")(T=T, Al=0.2, Nd=si("1e17 cm-3"))
        n_AlGaAs_BSF = material("AlGaAs")(T=T, Al=0.6,  Na=si("2e17 cm-3"))
        AlGaAs = material("AlGaAs")(T=T, Al=0.2, )

        n_GaAs = material('GaAs')(T=T, Nd=si('2e18 cm-3'), )
        p_GaAs = material("GaAs")(T=T, Na=si("2e19 cm-3"), )
        i_GaAs = material("GaAs")(T=T, valence_band_offset= si('-0.59 eV'))
        i_GaAs_barrier = material("GaAs")(T=T, strained=True, eff_mass_electron_Gamma=0.067
                                          , eff_mass_hh_z=0.51
                                          , eff_mass_lh_z=0.082
                                          , valence_band_offset= si('-0.59 eV')
                                          )
        InSb = material("InSb")(T=T
                                , strained=True
                                , electron_mobility=7.7
                                , hole_mobility=0.0850, valence_band_offset=si("0.0 eV")
                                , band_gap=si("0.173723 eV"), spin_orbit_splitting=si("0.81 eV")
                                , gamma1=34.8, gamma2=15.5, gamma3=16.5
                                , a_c=si("-6.94 eV"), a_v=si("-0.36 eV"), b=si("-2 eV")
                                )
        GaSb = material("GaSb")(T=T, strained=True, hole_mobility=0.09, electron_mobility=0.48)
        #Carrier Mobility in GaSb–V2Ga5and GaSb–GaV3Sb5 Eutectic Alloys
        #=============================================================================================
        #combine material
        QW = PDD.QWunit([
            # Layer(width=si(f"15 nm"), material=AlGaAs, role="barrier"),
            Layer(width=si("25 nm"), material=AlGaAs_stain, role="interlayer"),
            Layer(width=si(f"{dot} nm"), material=GaSb, role="well"),  # 5-20 nm
            Layer(width=si("25 nm"), material=AlGaAs_stain, role="interlayer"),
            # Layer(width=si(f"15 nm"), material=AlGaAs, role="barrier")
        ], T=T, repeat=5, substrate=AlGaAs, strain_calculation=True,)
        QW_list = QW.GetEffectiveQW(wavelengths=wl, use_Adachi=True)
        GaAs_junction = Junction([
                                     Layer(width=si("50 nm"), material=p_GaAs, role="contact"),
                                     Layer(width=si("30 nm"), material=p_AlGaAs_window, role="Emitter"),
                                     Layer(width=si("200 nm"), material=p_AlGaAs_enitter, role="Emitter"),
                                     Layer(width=si("175 nm"), material=AlGaAs, role="Emitter"),

                                 ]
                                 + QW_list
                                 # + QW_list
                                 + [
                                     Layer(width=si("175 nm"), material=AlGaAs, role="Emitter"),
                                     Layer(width=si("500 nm"), material=n_AlGaAs_base, role="Emitter"),
                                     Layer(width=si("100 nm"), material=n_AlGaAs_BSF, role="Emitter"),
                                     Layer(width=si("250 nm"), material=n_GaAs, role="Emitter"),

                                     # Layer(width=si("330 nm"), material=n_GaAs, role="Emitter"),
                                 ],
                                 T=T, kind="PDD", substrate=n_GaAs)
        GaAs_junction.parameters  = {'mode': 'steady-state',}
        my_solar_cell = SolarCell([
            GaAs_junction,
        ]
            , T=T, substrate=n_GaAs,)
        my_solar_cell.parameters ={'mode': 'steady-state',}
        solar_each_size_1[f"GaSb size ={dot} nm"] = my_solar_cell
    return solar_each_size_1, plot_note
#===========================================================================================================

def QDSC_InAs_GaSb():
    size_GaSbs = [5, 10, 15, 20]
    print(size_GaSbs)
    plot_note = dict(x_axis=size_GaSbs, x_axis_name="GaSb Dot size(nm)")
    solar_each_size_1 = {}
    for size_GaSb in size_GaSbs:
        size_InAs = 11
        size_GaSb = size_GaSb
        AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True, electron_mobility=si('300 cm2'))
        n_GaAs = material('GaAs')(T=T, Nd=si('1e18 cm-3'),  )
        i_GaAs = material("GaAs")(T=T)
        i_GaAs_barrier = material("GaAs")(T=T, strained=True, eff_mass_electron_Gamma=0.067
                                          , eff_mass_hh_z=0.51
                                          , eff_mass_lh_z=0.082)
        p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
        p_GaInP = material("GaInP")(T=T, In=0.42, Na=si("2e18 cm-3"))
        p_GaAs_buffer = material("GaAs")(T=T, Na=si("2e18 cm-3"))
        InSb = material("InSb")(T=T
                                , strained=True
                                , electron_mobility=7.7
                                , hole_mobility=0.0850, valence_band_offset=si("0.0 eV")
                                , band_gap=si("0.173723 eV"), spin_orbit_splitting=si("0.81 eV")
                                , gamma1=34.8, gamma2=15.5, gamma3=16.5
                                , a_c=si("-6.94 eV"), a_v=si("-0.36 eV"), b=si("-2 eV")
                                )
        InAs = material("INAS", sopra=True)(T=T,
                                            strained=True,
                                            valence_band_offset=si("-0.59 eV"),
                                            band_gap=si("0.417 eV"),
                                            eff_mass_electron=0.023,
                                            eff_mass_electron_Gamma=0.026,
                                            electron_mobility=si("3.5e4 cm2"),
                                            hole_mobility=si("5e2 cm2"),
                                            eff_mass_hh_z=0.64,
                                            eff_mass_lh_z=0.05,
                                            electron_affinity=si("4.9 eV"),
                                            gamma1=20,
                                            gamma2=8.5,
                                            gamma3=9.2,
                                            a_c=si("-5.08 eV"),
                                            a_v=si("-1 eV"),
                                            b=si("-1.8 eV"), d=si("-3.6 eV"),
                                            c11=si("832.9 GPa"),
                                            c12=si("452.6 GPa"),
                                            c44=si("395.9 GPa"),
                                            interband_matrix_element=si("22.2 eV"),
                                            spin_orbit_splitting=si("0.39 eV"),
                                            lattice_constant=6.0583e-10,
                                            electron_minority_lifetime=si("150 ps"),
                                            hole_minority_lifetime=si("1 nm"),
                                            relative_permittivity=15.15,
                                            electron_auger_recombination=si("1.6e-27 cm6"),
                                            hole_auger_recombination=si("1.6e-27 cm6"),
                                            )

        GaSb = material("GaSb")(T=T, strained=True,
                                electron_mobility=si("3e3 cm2"),
                                hole_mobility=si("1e3 cm2"),
                                )
        solar_each_size_1 = {}
        # interlayer = [5, 10, 15, 20, 25]
        QW = PDD.QWunit([
                            Layer(width=si(f"100 nm"), material=AlGaAs, role="barrier"),
                        ]
                        +
                        [Layer(width=si(f"50 nm"), material=i_GaAs, role="barrier"),
                         Layer(width=si(f"{size_GaSb} nm"), material=GaSb, role="well"),  # 5-20 nm
                         Layer(width=si(f"{5} nm"), material=i_GaAs, role="barrier"),
                         Layer(width=si(f"{size_InAs} nm"), material=InAs, role="well"), ]  # 5-20 nm
                        # Layer(width=si("20 nm"), material=i_GaAs, role="barrier"),]*dot

                        +
                        [Layer(width=si(f"100 nm"), material=AlGaAs, role="barrier")
                         ], T=T, repeat=1, substrate=i_GaAs)
        QW_list = QW.GetEffectiveQW(wavelengths=wl, use_Adachi=True)
        GaAs_junction = Junction([
                                     Layer(width=si("230 nm"), material=n_GaAs, role="Emitter"), ]
                                 + QW_list
                                 + [
                                     Layer(width=si("100 nm"), material=n_GaAs, role="Emitter"),
                                     Layer(width=si("2800 nm"), material=p_GaAs, role="Base"),
                                     Layer(width=si("100 nm"), material=p_GaInP, role="BSF"),
                                     Layer(width=si("150 nm"), material=p_GaAs_buffer, role="Buffer"),
                                 ],
                                 T=T, kind="PDD", substrate=p_GaAs)
        solarcell_InAs_GaSb = SolarCell([
            Layer(width=si("100 nm"), material=MgF2, role="AR1"),
            Layer(width=si("50 nm"), material=ZnS, role="AR2"),
            GaAs_junction,
        ]
            , T=T, substrate=p_GaAs)
        solar_each_size_1[f"size GaSb ={size_GaSbs} nm"] = solarcell_InAs_GaSb
    return solar_each_size_1, plot_note

# QDSC_InAs_GaSb()


def QDSC_GaSb_Sw_dotsize_interlayer():
    #define setup
    dot_size = [0.3, 0.9, 1.5, 2.1, 2.7, 3.1]
    interlayer = [50, 60, 70, 80, 90, 100]
    # modes = ['kp8x8_bulk']
    plot_note = dict( y_axis=dot_size,y_axis_name='dot size(nm)', x_axis=interlayer, x_axis_name='interlayer(nm)' )
    solar_each_all_axis = {}
    for y_axis in dot_size:
        solar_each_x_axis = {}
        for x_axis in interlayer:
            #define material
            AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True)
            n_GaAs = material('GaAs')(T=T, Nd=si('1e18 cm-3'), )
            i_GaAs = material("GaAs")(T=T)
            i_GaAs_barrier = material("GaAs")(T=T, strained=True, eff_mass_electron_Gamma=0.067
                                              , eff_mass_hh_z=0.51
                                              , eff_mass_lh_z=0.082)
            p_GaAs = material("GaAs")(T=T, Na=si("1e18 cm-3"), )
            InSb = material("InSb")(T=T
                                    , strained=True
                                    , electron_mobility=7.7
                                    , hole_mobility=0.0850, valence_band_offset=si("0.0 eV")
                                    , band_gap=si("0.173723 eV"), spin_orbit_splitting=si("0.81 eV")
                                    , gamma1=34.8, gamma2=15.5, gamma3=16.5
                                    , a_c=si("-6.94 eV"), a_v=si("-0.36 eV"), b=si("-2 eV")
                                    )
            GaSb = material("GaSb")(T=T, strained=True, )
            #=============================================================================================
            #combine material
            QW = PDD.QWunit([
                # Layer(width=si(f"15 nm"), material=AlGaAs, role="barrier"),
                Layer(width=si(f"{x_axis} nm"), material=i_GaAs_barrier, role="interlayer"),
                Layer(width=si(f"{y_axis} nm"), material=InSb, role="well"),  # 5-20 nm
                Layer(width=si(f"{x_axis} nm"), material=n_GaAs, role="interlayer"),
                # Layer(width=si(f"15 nm"), material=AlGaAs, role="barrier")
            ], T=T, repeat=1, substrate=i_GaAs)
            QW_list = QW.GetEffectiveQW(wavelengths=wl, use_Adachi=True)
            GaAs_junction = Junction([
                                         Layer(width=si("230 nm"), material=n_GaAs, role="Emitter"),
                                     ]
                                     + QW_list
                                     + [
                                         Layer(width=si("1700 nm"), material=p_GaAs, role="Emitter"),
                                     ],
                                     T=T, kind="PDD", substrate=p_GaAs)
            my_solar_cell = SolarCell([
                GaAs_junction,
            ]
                , T=T, substrate=p_GaAs)
            solar_each_x_axis[f"InSb interlayer = {x_axis} nm"] = my_solar_cell
        solar_each_all_axis[f'InSb dot = {y_axis} nm'] = solar_each_x_axis
    return solar_each_all_axis, plot_note

def ref_QDSC():
    # สร้างวัสดุทำรับQW ในsolar cell
    dot_size = range(1, 10, 1)
    # modes = ['kp8x8_bulk']
    print(dot_size)
    plot_note = dict(x_axis=dot_size, x_axis_name="stack")
    solar_each_size_1 = {}
    for dot in dot_size:

        QWmat = material("InGaAs")(T=T, In=0.2, strained=True)
        Bmat = material("GaAsP")(T=T, P=0.1, strained=True)
        i_GaAs = material("GaAs")(T=T)
        i_GaAs_dope = material("GaAs")(T=T, Na=1e14)

        # กำหนดโครงสร้างของwellให้มี3ชั้น 1ใช่GaAsP เป็น barrier 2ใช้internsic GaAs เป็นinterlayers 3 ใช้ InGaAs เป็นwell
        QW = PDD.QWunit(
            [
                Layer(width=5e-9, material=Bmat, role="barrier"),
                Layer(width=2e-9, material=i_GaAs, role="well"),
                Layer(width=6e-9, material=QWmat, role="well"),
                Layer(width=2e-9, material=i_GaAs, role="well"),
                Layer(width=5e-9, material=Bmat, role="barrier")
            ],
            T=T,

            repeat=dot,  #
            substrate=i_GaAs,
        )

        QW_list = QW.GetEffectiveQW(
            wavelengths=wl)  # optimic ให้QW ดีขึ้น(ไม่แน่ใจทำยังไง)เท่าที่เข้าใจคือมันปรับstrain ในband และปรับค่า absorption
        n_GaAs = material("GaAs")(T=T, Nd=1e24)
        p_GaAs = material("GaAs")(T=T, Na=8e22)

        GaAs_junction = Junction(
            [Layer(width=150e-9, material=n_GaAs, role="Emitter"), ]
            + QW_list
            + [Layer(width=2000e-9, material=p_GaAs, role="Base"), ],
            sn=1e6, sp=1e6, T=T, kind="PDD", )
        my_solar_cell = SolarCell([GaAs_junction, ],
                                  T=T, substrate=p_GaAs, )
        solar_each_size_1[f"stack ={dot}"] = my_solar_cell
    return solar_each_size_1, plot_note

def QDSC_InSb_GaSb_sweep_InSb():
    dot_size = np.linspace(0.5, 5, 50)
    plot_note = dict(x_axis=dot_size, x_axis_name="InSb Dot size(nm)")
    solar_each_size_1 = {}

    for i in dot_size:
        size_InSb = 2.5
        size_GaSb = 15
        AlGaAs = material("AlGaAs")(T=T, Al=0.3)
        n_GaAs = material('GaAs')(T=T, Nd=si('1e19 cm-3'), )
        n_GaAs_inter = material('GaAs')(T=T, Nd=si('1e17 cm-3'), )
        n_AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True, Nd=si("1e18 cm-3"))
        i_GaAs = material("GaAs")(T=T)
        p_GaInP = material("GaInP")(T=T, In=0.42, Na=si("2e18 cm-3"))
        p_GaAs_buffer = material("GaAs")(T=T, Na=si("2e18 cm-3"))
        p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
        InSb = material("InSb", sopra=True)(T=T
                                             , strained=True
                                             , valence_band_offset=si("0.0 eV")
                                             , band_gap=si("0.173723 eV")
                                             , lattice_constant=6.4793e-10
                                             , gamma1=34.8, gamma2=15.5, gamma3=16.6
                                             , a_c=si("-6.93 eV"), a_v=si("-0.36 eV"), b=si("-2 eV"), d=si("-4.7 eV")
                                             , c11=si("684.7 GPa"), c12=si("373.5 GPa"), c44=si("311.1 GPa")
                                             , interband_matrix_element=si("23.3 eV")
                                             , spin_orbit_splitting=si("0.81 eV")
                                             , eff_mass_electron_Gamma=0.0135
                                             , eff_mass_hh_z=0.05823949620355507
                                             , eff_mass_lh_z=0.0033633751606916276
                                             , eff_mass_electron=0.0022617432780656557
                                             , electron_mobility=si("78000 cm2")
                                             , hole_mobility=si("500 cm2")
                                             , electron_affinity=si("4.59 eV")
                                             , electron_minority_lifetime=si("1e-7 s")
                                             , hole_minority_lifetime=si("1e-8 s")
                                             , relative_permittivity=13.943
                                             , electron_auger_recombination=si("1e-42 cm6")
                                             , hole_auger_recombination=si("1e-42 cm6")
                                             )

        # GaSb = material("GaSb")(T=T, strained=True, hole_mobility=0.09, electron_mobility=0.48)
        GaSb = material("GaSb")(T=T, strained=True,
                                electron_mobility=si("3e3 cm2"),
                                hole_mobility=si("1e3 cm2"),
                                )

        QW = PDD.QWunit(
                  # [
                            # Layer(width=si(f"100 nm"), material=n_AlGaAs, role="barrier"),
                        # ]
                        # +
                        [
                        Layer(width=si(f"{100} nm"), material=i_GaAs, role="interlayer"),
                        Layer(width=si(f"{i} nm"), material=InSb, role="well"),
                        Layer(width=si(f"{100 - size_GaSb} nm"), material=i_GaAs, role="barrier"),
                        Layer(width=si(f"{size_GaSb} nm"), material=GaSb, role="well"),  # 5-20 nm
                        Layer(width=si(f"{50} nm"), material=i_GaAs, role="barrier"),
                         ]  # 5-20 nm
                        # Layer(width=si("20 nm"), material=i_GaAs, role="barrier"),]*dot

                        # +
                        # [Layer(width=si(f"100 nm"), material=n_AlGaAs, role="barrier")]
                        , T=T, repeat=5, substrate=i_GaAs)
        # E = 1240 / (wl * 1e9) * q
        # alpha_params = {
        #     "well_width": QW.QW_width,
        #     "theta": 0,
        #     "eps": 13.943 * vacuum_permittivity,
        #     "espace": E,
        #     "hwhm": si("6meV"),
        #     "dimensionality": 0.15,
        #     "line_shape": "Gauss"
        # }
        QW_list = QW.GetEffectiveQW(wavelengths=wl,
                                    use_Adachi=True,
                                    # blur=True,
                                    # blurmode="even",
                                    # periodic=False,
                                    # filter_strength=si('0.001 eV')
                                    # alpha_params=alpha_params,
                                    )
        # QW_list = QW.GetEffectiveQW(wavelengths=wl, use_Adachi=True)
        GaAs_junction = Junction([
                                     Layer(width=si("300 nm"), material=n_GaAs, role="Emitter"),
                                     # Layer(width=si(f"100 nm"), material=n_AlGaAs, role="barrier"),
                                 ]
                                 + QW_list
                                 + [
                                     # Layer(width=si(f"100 nm"), material=n_AlGaAs, role="barrier"),
                                     # Layer(width=si("100 nm"), material=n_GaAs, role="Emitter"),
                                     Layer(width=si("1800 nm"), material=p_GaAs, role="Base"),
                                     # Layer(width=si("100 nm"), material=p_GaInP, role="BSF"),
                                     # Layer(width=si("150 nm"), material=p_GaAs_buffer, role="Buffer"),
                                 ],
                                 T=T, kind="PDD", substrate=p_GaAs)
        solarcell_InSb_GaSb = SolarCell([
            # Layer(width=si("100 nm"), material=MgF2, role="AR1"),
            # Layer(width=si("50 nm"), material=ZnS, role="AR2"),
            GaAs_junction,
        ]
            , T=T, substrate=p_GaAs)
        solar_each_size_1[f"InSb dot size ={i} (nm)"] = solarcell_InSb_GaSb
    return solar_each_size_1, plot_note

def QDSC_InSb_GaSb_sweep_stack():
    dot_size = np.arange(1, 11, 1)
    plot_note = dict(x_axis=dot_size, x_axis_name="stack")
    solar_each_size_1 = {}

    for i in dot_size:
        size_InSb = 15
        size_GaSb = 15
        AlGaAs = material("AlGaAs")(T=T, Al=0.3)
        n_GaAs = material('GaAs')(T=T, Nd=si('1e19 cm-3'), )
        n_GaAs_inter = material('GaAs')(T=T, Nd=si('1e17 cm-3'), )
        n_AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True, Nd=si("1e18 cm-3"))
        i_GaAs = material("GaAs")(T=T)
        p_GaInP = material("GaInP")(T=T, In=0.42, Na=si("2e18 cm-3"))
        p_GaAs_buffer = material("GaAs")(T=T, Na=si("2e18 cm-3"))
        p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
        InSb = material("InSb", sopra=True)(T=T
                                             , strained=True
                                             , valence_band_offset=si("0.0 eV")
                                             , band_gap=si("0.173723 eV")
                                             , lattice_constant=6.4793e-10
                                             , gamma1=34.8, gamma2=15.5, gamma3=16.6
                                             , a_c=si("-6.93 eV"), a_v=si("-0.36 eV"), b=si("-2 eV"), d=si("-4.7 eV")
                                             , c11=si("684.7 GPa"), c12=si("373.5 GPa"), c44=si("311.1 GPa")
                                             , interband_matrix_element=si("23.3 eV")
                                             , spin_orbit_splitting=si("0.81 eV")
                                             , eff_mass_electron_Gamma=0.0135
                                             , eff_mass_hh_z=0.05823949620355507
                                             , eff_mass_lh_z=0.0033633751606916276
                                             , eff_mass_electron=0.0022617432780656557
                                             , electron_mobility=si("78000 cm2")
                                             , hole_mobility=si("500 cm2")
                                             , electron_affinity=si("4.59 eV")
                                             , electron_minority_lifetime=si("1e-6 s")
                                             , hole_minority_lifetime=si("1e-8 s")
                                             , relative_permittivity=13.943
                                             , electron_auger_recombination=si("1e-42 cm6")
                                             , hole_auger_recombination=si("1e-42 cm6")
                                             )

        # GaSb = material("GaSb")(T=T, strained=True, hole_mobility=0.09, electron_mobility=0.48)
        GaSb = material("GaSb")(T=T, strained=True,
                                electron_mobility=si("3e3 cm2"),
                                hole_mobility=si("1e3 cm2"),
                                )

        QW = PDD.QWunit(
                  # [
                            # Layer(width=si(f"100 nm"), material=n_AlGaAs, role="barrier"),
                        # ]
                        # +
                        [
                        Layer(width=si(f"{100} nm"), material=i_GaAs, role="interlayer"),
                        Layer(width=si(f"{size_InSb} nm"), material=InSb, role="well"),
                        Layer(width=si(f"{100 - size_GaSb} nm"), material=i_GaAs, role="barrier"),
                        Layer(width=si(f"{size_GaSb} nm"), material=GaSb, role="well"),  # 5-20 nm
                        Layer(width=si(f"{50} nm"), material=i_GaAs, role="barrier"),
                         ]  # 5-20 nm
                        # Layer(width=si("20 nm"), material=i_GaAs, role="barrier"),]*dot

                        # +
                        # [Layer(width=si(f"100 nm"), material=n_AlGaAs, role="barrier")]
                        , T=T, repeat=i, substrate=i_GaAs)
        E = 1240 / (wl * 1e9) * q
        alpha_params = {
            "well_width": QW.QW_width,
            "theta": 0,
            "eps": 13.943 * vacuum_permittivity,
            "espace": E,
            "hwhm": si("6meV"),
            "dimensionality": 0.15,
            "line_shape": "Gauss"
        }
        QW_list = QW.GetEffectiveQW(wavelengths=wl,
                                    use_Adachi=True,
                                    # blur=True,
                                    # blurmode="even",
                                    # periodic=False,
                                    # filter_strength=si('0.001 eV')
                                    # alpha_params=alpha_params,
                                    )
        # QW_list = QW.GetEffectiveQW(wavelengths=wl, use_Adachi=True)
        GaAs_junction = Junction([
                                     Layer(width=si("300 nm"), material=n_GaAs, role="Emitter"),
                                     # Layer(width=si(f"100 nm"), material=n_AlGaAs, role="barrier"),
                                 ]
                                 + QW_list
                                 + [
                                     # Layer(width=si(f"100 nm"), material=n_AlGaAs, role="barrier"),
                                     # Layer(width=si("100 nm"), material=n_GaAs, role="Emitter"),
                                     Layer(width=si("1800 nm"), material=p_GaAs, role="Base"),
                                     # Layer(width=si("100 nm"), material=p_GaInP, role="BSF"),
                                     # Layer(width=si("150 nm"), material=p_GaAs_buffer, role="Buffer"),
                                 ],
                                 T=T, kind="PDD", substrate=p_GaAs)
        solarcell_InSb_GaSb = SolarCell([
            # Layer(width=si("100 nm"), material=MgF2, role="AR1"),
            # Layer(width=si("50 nm"), material=ZnS, role="AR2"),
            GaAs_junction,
        ]
            , T=T, substrate=p_GaAs)
        solar_each_size_1[f"dot stack = {i} "] = solarcell_InSb_GaSb
    return solar_each_size_1, plot_note

def QDSC_InSb_GaSb_sweep_InSb_AlGaAs():
    dot_size = np.linspace(5, 50, 5)
    plot_note = dict(x_axis=dot_size, x_axis_name="InSb Dot size(nm)")
    solar_each_size_1 = {}

    for i in dot_size:
        size_GaSb = 15
        AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True)
        n_GaAs = material('GaAs')(T=T, Nd=si('1e19 cm-3'), )
        n_AlGaAs = material("AlGaAs")(T=T, Al=0.3, Nd=si("1e18 cm-3"))
        i_GaAs = material("GaAs")(T=T)
        p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
        InSb = material("InSb", sopra=True)(T=T
                                             , strained=True
                                             , valence_band_offset=si("0.0 eV")
                                             , band_gap=si("0.173723 eV")
                                             , lattice_constant=6.4793e-10
                                             , gamma1=34.8, gamma2=15.5, gamma3=16.6
                                             , a_c=si("-6.93 eV"), a_v=si("-0.36 eV"), b=si("-2 eV"), d=si("-4.7 eV")
                                             , c11=si("684.7 GPa"), c12=si("373.5 GPa"), c44=si("311.1 GPa")
                                             , interband_matrix_element=si("23.3 eV")
                                             , spin_orbit_splitting=si("0.81 eV")
                                             , eff_mass_electron_Gamma=0.0135
                                             , eff_mass_hh_z=0.05823949620355507
                                             , eff_mass_lh_z=0.0033633751606916276
                                             , eff_mass_electron=0.0022617432780656557
                                             , electron_mobility=si("78000 cm2")
                                             , hole_mobility=si("500 cm2")
                                             , electron_affinity=si("4.59 eV")
                                             , electron_minority_lifetime=si("1e-7 s")
                                             , hole_minority_lifetime=si("1e-8 s")
                                             , relative_permittivity=13.943
                                             , electron_auger_recombination=si("1e-42 cm6")
                                             , hole_auger_recombination=si("1e-42 cm6")
                                             )

        # GaSb = material("GaSb")(T=T, strained=True, hole_mobility=0.09, electron_mobility=0.48)
        GaSb = material("GaSb")(T=T, strained=True,
                                electron_mobility=si("3e3 cm2"),
                                hole_mobility=si("1e3 cm2"),
                                )

        QW = PDD.QWunit(
                  # [
                  #           Layer(width=si(f"100 nm"), material=AlGaAs, role="barrier"),
                  #       ]
                  #       +
                        [
                        Layer(width=si(f"{100} nm"), material=i_GaAs, role="interlayer"),
                        Layer(width=si(f"{i} nm"), material=InSb, role="well"),
                        Layer(width=si(f"{100 - size_GaSb} nm"), material=i_GaAs, role="interlayer"),
                        Layer(width=si(f"{size_GaSb} nm"), material=GaSb, role="well"),  # 5-20 nm
                        Layer(width=si(f"{50} nm"), material=i_GaAs, role="barrier"),
                        ]  # 5-20 nm
                        # Layer(width=si("20 nm"), material=i_GaAs, role="barrier"),]*dot
                        # +
                        # [Layer(width=si(f"100 nm"), material=AlGaAs, role="barrier")]
                        , T=T, repeat=10, substrate=i_GaAs)
        # E = 1240 / (wl * 1e9) * q
        # alpha_params = {
        #     "well_width": QW.QW_width,
        #     "theta": 0,
        #     "eps": 13.943 * vacuum_permittivity,
        #     "espace": E,
        #     "hwhm": si("6meV"),
        #     "dimensionality": 0.15,
        #     "line_shape": "Gauss"
        # }
        QW_list = QW.GetEffectiveQW(wavelengths=wl,
                                    use_Adachi=True,
                                    # blur=True,
                                    # blurmode="even",
                                    periodic=False,
                                    # filter_strength=si('0.001 eV')
                                    # alpha_params=alpha_params,
                                    )
        GaAs_junction = Junction([
                                     Layer(width=si("200 nm"), material=n_GaAs, role="Emitter"),
                                     # Layer(width=si(f"{50} nm"), material=i_GaAs, role="interlayer"),
                                     Layer(width=si(f"100 nm"), material=AlGaAs, role="barrier"),

                                 ]
                                 + QW_list
                                 + [
                                     Layer(width=si(f"100 nm"), material=AlGaAs, role="barrier"),
                                     # Layer(width=si(f"{50} nm"), material=i_GaAs, role="interlayer"),
                                     # Layer(width=si("100 nm"), material=n_GaAs_bot, role="Emitter"),
                                     Layer(width=si("1800 nm"), material=p_GaAs, role="Base"),
                                     # Layer(width=si("100 nm"), material=p_GaInP, role="BSF"),
                                     # Layer(width=si("150 nm"), material=p_GaAs_buffer, role="Buffer"),
                                 ],
                                 T=T, kind="PDD", substrate=p_GaAs)
        solarcell_InSb_GaSb = SolarCell([
            # Layer(width=si("100 nm"), material=MgF2, role="AR1"),
            # Layer(width=si("50 nm"), material=ZnS, role="AR2"),
            GaAs_junction,
        ]
            , T=T, substrate=p_GaAs)
        solar_each_size_1[f"InSb dot size = {i:.2e} (nm)"] = solarcell_InSb_GaSb
    return solar_each_size_1, plot_note

def QDSC_InSb_GaSb_sweep_stack_AlGaAs():
    dot_size = np.arange(1, 10, 1)
    plot_note = dict(x_axis=dot_size, x_axis_name="stack")
    solar_each_size_1 = {}

    for i in dot_size:
        size_InSb = 5
        size_GaSb = 15
        AlGaAs = material("AlGaAs")(T=T, Al=0.3)
        n_GaAs = material('GaAs')(T=T, Nd=si('1e16 cm-3'), )
        n_GaAs_bot = material('GaAs')(T=T, Nd=si('1e15 cm-3'))

        n_GaAs_inter = material('GaAs')(T=T, Nd=si('1e17 cm-3'), )
        n_AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True, Nd=si("1e18 cm-3"))
        i_GaAs = material("GaAs")(T=T)
        p_GaInP = material("GaInP")(T=T, In=0.42, Na=si("2e18 cm-3"))
        p_GaAs_buffer = material("GaAs")(T=T, Na=si("2e18 cm-3"))
        p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
        InSb = material("InSb", sopra=True)(T=T
                                             , strained=True
                                             , valence_band_offset=si("0.0 eV")
                                             , band_gap=si("0.173723 eV")
                                             , lattice_constant=6.4793e-10
                                             , gamma1=34.8, gamma2=15.5, gamma3=16.6
                                             , a_c=si("-6.93 eV"), a_v=si("-0.36 eV"), b=si("-2 eV"), d=si("-4.7 eV")
                                             , c11=si("684.7 GPa"), c12=si("373.5 GPa"), c44=si("311.1 GPa")
                                             , interband_matrix_element=si("23.3 eV")
                                             , spin_orbit_splitting=si("0.81 eV")
                                             , eff_mass_electron_Gamma=0.0135
                                             , eff_mass_hh_z=0.05823949620355507
                                             , eff_mass_lh_z=0.0033633751606916276
                                             , eff_mass_electron=0.0022617432780656557
                                             , electron_mobility=si("78000 cm2")
                                             , hole_mobility=si("500 cm2")
                                             , electron_affinity=si("4.59 eV")
                                             , electron_minority_lifetime=si("1e-6 s")
                                             , hole_minority_lifetime=si("1e-8 s")
                                             , relative_permittivity=13.943
                                             , electron_auger_recombination=si("1e-42 cm6")
                                             , hole_auger_recombination=si("1e-42 cm6")
                                             )

        # GaSb = material("GaSb")(T=T, strained=True, hole_mobility=0.09, electron_mobility=0.48)
        GaSb = material("GaSb")(T=T, strained=True,
                                electron_mobility=si("3e3 cm2"),
                                hole_mobility=si("1e3 cm2"),
                                )

        QW = PDD.QWunit(
                  [
                            Layer(width=si(f"100 nm"), material=AlGaAs, role="barrier"),
                        ]
                        +
                        [
                        Layer(width=si(f"{100} nm"), material=i_GaAs, role="interlayer"),
                        Layer(width=si(f"{size_InSb} nm"), material=InSb, role="well"),
                        Layer(width=si(f"{100 - size_GaSb} nm"), material=i_GaAs, role="barrier"),
                        Layer(width=si(f"{size_GaSb} nm"), material=GaSb, role="well"),  # 5-20 nm
                        Layer(width=si(f"{50} nm"), material=i_GaAs, role="barrier"),
                         ] * i  # 5-20 nm
                        # Layer(width=si("20 nm"), material=i_GaAs, role="barrier"),]*dot

                        +
                        [Layer(width=si(f"100 nm"), material=AlGaAs, role="barrier")]
                        , T=T, repeat=1, substrate=i_GaAs)

        QW_list = QW.GetEffectiveQW(wavelengths=wl,
                                    use_Adachi=True,
                                    )
        # QW_list = QW.GetEffectiveQW(wavelengths=wl, use_Adachi=True)
        GaAs_junction = Junction([
                                      Layer(width=si("100 nm"), material=n_GaAs, role="Emitter"),
                                     # Layer(width=si(f"{50} nm"), material=i_GaAs, role="interlayer"),

                                     # Layer(width=si(f"100 nm"), material=n_AlGaAs, role="barrier"),
                                 ]
                                 + QW_list
                                 + [
                                     # Layer(width=si(f"{50} nm"), material=i_GaAs, role="interlayer"),
                                     # Layer(width=si(f"100 nm"), material=n_AlGaAs, role="barrier"),
                                     # Layer(width=si("100 nm"), material=n_GaAs_bot, role="Emitter"),
                                     Layer(width=si("1800 nm"), material=p_GaAs, role="Base"),
                                     # Layer(width=si("100 nm"), material=p_GaInP, role="BSF"),
                                     # Layer(width=si("150 nm"), material=p_GaAs_buffer, role="Buffer"),
                                 ],
                                 T=T, kind="PDD", substrate=p_GaAs)
        solarcell_InSb_GaSb = SolarCell([
            # Layer(width=si("100 nm"), material=MgF2, role="AR1"),
            # Layer(width=si("50 nm"), material=ZnS, role="AR2"),
            GaAs_junction,
        ]
            , T=T, substrate=p_GaAs)
        solar_each_size_1[f"dot stack = {i} "] = solarcell_InSb_GaSb
    return solar_each_size_1, plot_note
def solar_cell_InSb_and_GaSb_like_paper():
    solar_each_size_1 = {}
    plot_note = dict(x_axis=[1, 2,], x_axis_name="DOT_VS_bulk", x_axis_txt="InSb&GaSb  GaSb bulk")
    def get_GaSb_InSb():
        size_InSb = 1
        size_GaSb = 15
        AlGaAs = material("AlGaAs")(T=T, Al=0.3)
        n_GaAs = material('GaAs')(T=T, Nd=si('1e19 cm-3'), )
        n_GaAs_min = material('GaAs')(T=T, Nd=si('1e17 cm-3'), )
        n_GaAs_inter = material('GaAs')(T=T, Nd=si('1e17 cm-3'), )
        n_AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True, Nd=si("1e18 cm-3"))
        i_GaAs = material("GaAs")(T=T)
        p_GaInP = material("GaInP")(T=T, In=0.42, Na=si("2e18 cm-3"))
        p_GaAs_buffer = material("GaAs")(T=T, Na=si("2e18 cm-3"))
        p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
        InSb = material("InSb", sopra=True)(T=T
                                            , strained=True
                                            , valence_band_offset=si("0.0 eV")
                                            , band_gap=si("0.173723 eV")
                                            , lattice_constant=6.4793e-10
                                            , gamma1=34.8, gamma2=15.5, gamma3=16.6
                                            , a_c=si("-6.93 eV"), a_v=si("-0.36 eV"), b=si("-2 eV"), d=si("-4.7 eV")
                                            , c11=si("684.7 GPa"), c12=si("373.5 GPa"), c44=si("311.1 GPa")
                                            , interband_matrix_element=si("23.3 eV")
                                            , spin_orbit_splitting=si("0.81 eV")
                                            , eff_mass_electron_Gamma=0.0135
                                            , eff_mass_hh_z=0.05823949620355507
                                            , eff_mass_lh_z=0.0033633751606916276
                                            , eff_mass_electron=0.0022617432780656557
                                            , electron_mobility=si("78000 cm2")
                                            , hole_mobility=si("500 cm2")
                                            , electron_affinity=si("4.59 eV")
                                            , electron_minority_lifetime=si("1e-6 s")
                                            , hole_minority_lifetime=si("1e-8 s")
                                            , relative_permittivity=13.943
                                            , electron_auger_recombination=si("1e-42 cm6")
                                            , hole_auger_recombination=si("1e-42 cm6")
                                            )

        # GaSb = material("GaSb")(T=T, strained=True, hole_mobility=0.09, electron_mobility=0.48)
        GaSb = material("GaSb")(T=T, strained=True,
                                electron_mobility=si("3e3 cm2"),
                                hole_mobility=si("1e3 cm2"),
                                )

        QW = PDD.QWunit(
            # [
            # Layer(width=si(f"100 nm"), material=n_AlGaAs, role="barrier"),
            # ]
            # +
            [
                Layer(width=si(f"{100} nm"), material=i_GaAs, role="interlayer"),
                Layer(width=si(f"{size_InSb} nm"), material=InSb, role="well"),
                Layer(width=si(f"{100 - size_GaSb} nm"), material=i_GaAs, role="barrier"),
                Layer(width=si(f"{size_GaSb} nm"), material=GaSb, role="well"),  # 5-20 nm
                Layer(width=si(f"{50} nm"), material=i_GaAs, role="barrier"),
            ]  # 5-20 nm
            , T=T, repeat=1, substrate=i_GaAs)
        E = 1240 / (wl * 1e9) * q
        alpha_params = {
            "well_width": QW.QW_width,
            "theta": 0,
            "eps": 12.9 * vacuum_permittivity,
            "espace": E,
            "hwhm": si("4meV"),
            "dimensionality": 0.15,
            "line_shape": "Lorenzian"
        }
        QW_list = QW.GetEffectiveQW(wavelengths=wl,
                                    use_Adachi=True,
                                    # blur=True,
                                    # blurmode="even",
                                    # periodic=False,
                                    # filter_strength=si('0.001 eV')
                                    # alpha_params=alpha_params,
                                    )
        # QW_list = QW.GetEffectiveQW(wavelengths=wl, use_Adachi=True)
        GaAs_junction = Junction([
                                     Layer(width=si("200 nm"), material=n_GaAs, role="Emitter"),
                                     Layer(width=si("100 nm"), material=n_GaAs_min, role="Emitter"),

                                     # Layer(width=si(f"100 nm"), material=n_AlGaAs, role="barrier"),

                                 ]
                                 + QW_list
                                 + [
                                     # Layer(width=si(f"100 nm"), material=n_AlGaAs, role="barrier"),
                                     # Layer(width=si("100 nm"), material=n_GaAs, role="Emitter"),
                                     Layer(width=si("1800 nm"), material=p_GaAs, role="Base"),
                                     # Layer(width=si("100 nm"), material=p_GaInP, role="BSF"),
                                     # Layer(width=si("150 nm"), material=p_GaAs_buffer, role="Buffer"),
                                 ],
                                 T=T, kind="PDD", substrate=p_GaAs)
        solarcell_InSb_GaSb = SolarCell([
            # Layer(width=si("100 nm"), material=MgF2, role="AR1"),
            # Layer(width=si("50 nm"), material=ZnS, role="AR2"),
            GaAs_junction,
        ]
            , T=T, substrate=p_GaAs)
        return solarcell_InSb_GaSb
    solar_each_size_1[f"QDSC_InSb_GaSb"] = get_GaSb_InSb()
    #
    def get_Dot_in_a_well():
        size_InSb = 1
        size_GaSb = 15

        n_GaAs = material('GaAs')(T=T, Nd=si('1e17 cm-3'), )
        i_GaAs = material("GaAs")(T=T)
        n_AlGaAs = material("AlGaAs")(T=T, Al=0.3, Nd=si("1e16"))
        p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
        InSb = material("InSb", sopra=True)(T=T
                                            , strained=True
                                            , valence_band_offset=si("0.0 eV")
                                            , band_gap=si("0.173723 eV")
                                            , lattice_constant=6.4793e-10
                                            , gamma1=34.8, gamma2=15.5, gamma3=16.6
                                            , a_c=si("-6.93 eV"), a_v=si("-0.36 eV"), b=si("-2 eV"), d=si("-4.7 eV")
                                            , c11=si("684.7 GPa"), c12=si("373.5 GPa"), c44=si("311.1 GPa")
                                            , interband_matrix_element=si("23.3 eV")
                                            , spin_orbit_splitting=si("0.81 eV")
                                            , eff_mass_electron_Gamma=0.0135
                                            , eff_mass_hh_z=0.05823949620355507
                                            , eff_mass_lh_z=0.0033633751606916276
                                            , eff_mass_electron=0.0022617432780656557
                                            , electron_mobility=si("78000 cm2")
                                            , hole_mobility=si("500 cm2")
                                            , electron_affinity=si("4.59 eV")
                                            , electron_minority_lifetime=si("1e-6 s")
                                            , hole_minority_lifetime=si("1e-8 s")
                                            , relative_permittivity=13.943
                                            , electron_auger_recombination=si("1e-42 cm6")
                                            , hole_auger_recombination=si("1e-42 cm6")
                                            )
        GaSb = material("GaSb")(T=T, strained=True,
                                electron_mobility=si("3e3 cm2"),
                                hole_mobility=si("1e3 cm2"),
                                )
        QW = PDD.QWunit(
            [
                Layer(width=si(f"{100} nm"), material=i_GaAs, role="interlayer"),
                Layer(width=si(f"{size_GaSb} nm"), material=GaSb, role="well"),
                Layer(width=si(f"{size_InSb} nm"), material=InSb, role="well"),  # 5-20 nm
                Layer(width=si(f"{size_GaSb} nm"), material=GaSb, role="well"),
                Layer(width=si(f"{100} nm"), material=i_GaAs, role="barrier"),

            ]  # 5-20 nm
            , T=T, repeat=1, substrate=i_GaAs)
        QW_list = QW.GetEffectiveQW(wavelengths=wl,
                                    use_Adachi=True,
                                    )
        GaAs_junction = Junction([
                                     Layer(width=si("30 nm"), material=n_GaAs, role="Emitter"),
                                 ]
                                 + QW_list
                                 + [
                                     Layer(width=si("100 nm"), material=n_GaAs, role="Emitter"),
                                     Layer(width=si("1800 nm"), material=p_GaAs, role="Base"),
                                 ],
                                 T=T, kind="PDD", substrate=p_GaAs, sn=0, sp=0)
        solarcell_InSb = SolarCell([
            GaAs_junction,
        ]
            , T=T, substrate=p_GaAs)
        return solarcell_InSb
    # solar_each_size_1[f"QDSC_InSb_in_well"] = get_Dot_in_a_well()
    def get_GaSb():
        AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True)
        n_GaAs = material('GaAs')(T=T, Nd=si('1e18 cm-3'), )
        i_GaAs_barrier = material("GaAs")(T=T, strained=True, eff_mass_electron_Gamma=0.067
                                          , eff_mass_hh_z=0.51
                                          , eff_mass_lh_z=0.082)
        i_GaAs_strain_free = material("GaAs")(T=T)
        p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
        GaSb = material("GaSb")(T=T, strained=True,
                                electron_mobility=si("3e3 cm2"),
                                hole_mobility=si("1e3 cm2"),
                                )
        size_GaSb = 15

        QW = PDD.QWunit(
            [
                Layer(width=si("15 nm"), material=AlGaAs, role="barrier"),
                Layer(width=si("10 nm"), material=i_GaAs_barrier, role="interlayer"),
                Layer(width=si(f"{size_GaSb} nm"), material=GaSb, role="well"),  # 5-20 nm
                Layer(width=si("10 nm"), material=i_GaAs_barrier, role="interlayer"),
                Layer(width=si("15 nm"), material=AlGaAs, role="barrier"),

            ]  # 5-20 nm
            , T=T, repeat=3, substrate=i_GaAs_strain_free)
        QW_list = QW.GetEffectiveQW(wavelengths=wl, use_Adachi=True)
        GaAs_junction = Junction([
                                     Layer(width=si("50 nm"), material=n_GaAs, role="Emitter"),]
                                 + QW_list
                                 + [
                                     Layer(width=si("2800 nm"), material=p_GaAs, role="Base"),
                                 ],
                                 T=T, kind="PDD", substrate=p_GaAs,sn=0, sp=0)
        solarcell_GaSb = SolarCell([
            GaAs_junction,
        ]
            , T=T, substrate=p_GaAs)
        return solarcell_GaSb
    # solar_each_size_1[f"QDSC_GaSb"] = get_GaSb()

    # size_InAs = 11
    # size_GaSb = 15
    # AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True)
    # n_GaAs = material('GaAs')(T=T, Nd=si('1e18 cm-3'), )
    # i_GaAs = material("GaAs")(T=T)
    # p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
    # p_GaInP = material("GaInP")(T=T, In=0.42, Na=si("2e18 cm-3"))
    # p_GaAs_buffer = material("GaAs")(T=T, Na=si("2e18 cm-3"))
    #
    # InAs = material("INAS", sopra=True)(T=T, strained=True,
    #                                     valence_band_offset=si("-0.59 eV"),
    #                                     band_gap=si("0.417 eV"),
    #                                     eff_mass_electron=0.023,
    #                                     eff_mass_electron_Gamma=0.026,
    #                                     electron_mobility=si("3.5e4 cm2"),
    #                                     hole_mobility=si("5e2 cm2"),
    #                                     eff_mass_hh_z=0.64,
    #                                     eff_mass_lh_z=0.05,
    #                                     electron_affinity=si("4.9 eV"),
    #                                     gamma1=20, gamma2=8.5, gamma3=9.2,
    #                                     a_c=si("-5.08 eV"), a_v=si("-1 eV"), b=si("-1.8 eV"), d=si("-3.6 eV"),
    #                                     c11=si("832.9 GPa"), c12=si("452.6 GPa"), c44=si("395.9 GPa"),
    #                                     interband_matrix_element=si("22.2 eV"),
    #                                     spin_orbit_splitting=si("0.39 eV"),
    #                                     lattice_constant=6.0583e-10,
    #                                     electron_minority_lifetime=si("150 ps"),
    #                                     hole_minority_lifetime=si("1 nm"),
    #                                     relative_permittivity=15.15,
    #                                     electron_auger_recombination=si("15e-30 cm6"),
    #                                     hole_auger_recombination=si("15e-31 cm6"),
    #                                     )
    #
    # GaSb = material("GaSb")(T=T, strained=True,
    #                         electron_mobility=si("3e3 cm2"),
    #                         hole_mobility=si("1e3 cm2"),
    #                         )
    # QW = PDD.QWunit([
    #                     Layer(width=si(f"100 nm"), material=AlGaAs, role="barrier"),
    #                 ]
    #                 +
    #                 [Layer(width=si(f"50 nm"), material=i_GaAs, role="barrier"),
    #                  Layer(width=si(f"{size_GaSb} nm"), material=GaSb, role="well"),  # 5-20 nm
    #                  Layer(width=si(f"{10} nm"), material=i_GaAs, role="barrier"),
    #                  Layer(width=si(f"{size_InAs} nm"), material=InAs, role="well"), ]  # 5-20 nm
    #                 # Layer(width=si("20 nm"), material=i_GaAs, role="barrier"),]*dot
    #
    #                 +
    #                 [Layer(width=si(f"100 nm"), material=AlGaAs, role="barrier")
    #                  ], T=T, repeat=1, substrate=i_GaAs)
    # QW_list = QW.GetEffectiveQW(wavelengths=wl, use_Adachi=True)
    # GaAs_junction = Junction([
    #                              Layer(width=si("230 nm"), material=n_GaAs, role="Emitter"), ]
    #                          + QW_list
    #                          + [
    #                              Layer(width=si("100 nm"), material=n_GaAs, role="Emitter"),
    #                              Layer(width=si("2800 nm"), material=p_GaAs, role="Base"),
    #                              Layer(width=si("100 nm"), material=p_GaInP, role="BSF"),
    #                              Layer(width=si("150 nm"), material=p_GaAs_buffer, role="Buffer"),
    #                          ],
    #                          T=T, kind="PDD", substrate=p_GaAs, sn=0, sp=0)
    # solarcell_InAs_GaSb = SolarCell([
    #     # Layer(width=si("100 nm"), material=MgF2, role="AR1"),
    #     # Layer(width=si("50 nm"), material=ZnS, role="AR2"),
    #     GaAs_junction,
    # ]
    #     , T=T, substrate=p_GaAs)
    # solar_each_size_1[f"QDSC_InAs_GaSb"] = solarcell_InAs_GaSb
    #
    def get_GaAs():
        n_GaAs = material('GaAs')(T=T, Nd=si('1e18 cm-3'), )
        p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )

        GaAs_junction = Junction([
                                     Layer(width=si("300 nm"), material=n_GaAs, role="Emitter"), ]
                                 + [
                                     # Layer(width=si("100 nm"), material=n_GaAs, role="Emitter"),
                                     Layer(width=si("1800 nm"), material=p_GaAs, role="Base"),
                                     # Layer(width=si("100 nm"), material=p_GaInP, role="BSF"),
                                     # Layer(width=si("150 nm"), material=p_GaAs_buffer, role="Buffer"),
                                 ],
                                 T=T, kind="PDD", substrate=p_GaAs)
        solarcell = SolarCell([
            # Layer(width=si("100 nm"), material=MgF2, role="AR1"),
            # Layer(width=si("50 nm"), material=ZnS, role="AR2"),
            GaAs_junction,
        ]
            , T=T, substrate=p_GaAs)
        return solarcell
    solar_each_size_1[f"SC_GaAs"] = get_GaAs()

    return solar_each_size_1, plot_note

if __name__ == '__main__':
    print(si('68.47 GPa'))

    # from solcore.units_system import siUnits
    from solcore import get_parameter
    print('this is material_and_layer_QD.py file')
    # InSb_dot_size_sweep(show=True)
    # AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True)
    # i_GaAs = material("GaAs")(T=T, strained=True, band_gap=si("1.422 eV"))
    GaAs = material("GaAs")(T=T
                            , strained=False
                            # , electron_mobility=7.7
                            # , hole_mobility=0.0850, valence_band_offset=si("0.0 eV")
                            # , band_gap=si("0.173723 eV"), spin_orbit_splitting=si("0.81 eV")
                            # , gamma1=34.8, gamma2=15.5, gamma3=16.5
                            # , a_c=si("-6.94"), a_v=si("-0.36 eV"), b=si("-2 eV")

                            )

    # print(dict(GaAs))
    atts = ['valence_band_offset','band_gap','eff_mass_electron','eff_mass_electron_Gamma','electron_mobility','hole_mobility','eff_mass_hh_z','eff_mass_lh_z','electron_affinity','gamma1','gamma2','gamma3','a_c','a_v','b','c11','c12','c44','interband_matrix_element','spin_orbit_splitting','lattice_constant','electron_minority_lifetime','hole_minority_lifetime','relative_permittivity','electron_auger_recombination','hole_auger_recombination',]
    # for attrname in atts:
        # print(attrname)
    #
    # atts = []
    # print('-----------------------------------------')
    # print('band_gap')
    # print(GaAs.band_gap)
    # print(asUnit(GaAs.band_gap, 'eV'))
    # print('-----------------------------------------')
    # print('T')
    # print(GaAs.T)
    # print('-----------------------------------------')
    # print('strained')
    # print(GaAs.strained)
    # print('-----------------------------------------')
    # print('valence_band_offset')
    # print(GaAs.valence_band_offset)
    # print(asUnit(GaAs.valence_band_offset, 'eV'))
    # print('-----------------------------------------')
    # print('eff_mass_electron')
    # print(GaAs.eff_mass_electron)
    # print('-----------------------------------------')
    # print('eff_mass_electron_Gamma')
    # print(GaAs.eff_mass_electron_Gamma)
    # print('-----------------------------------------')
    # print('electron_mobility')
    # print(GaAs.electron_mobility)
    # print('-----------------------------------------')
    # print('hole_mobility')
    # print(GaAs.hole_mobility)
    # print('-----------------------------------------')
    # print('eff_mass_hh_z')
    # print(GaAs.eff_mass_hh_z)
    # print('-----------------------------------------')
    # print('eff_mass_lh_z')
    # print(GaAs.eff_mass_lh_z)
    # print('-----------------------------------------')
    # print('electron_affinity')
    # print(GaAs.electron_affinity)
    # print(asUnit(GaAs.electron_affinity, 'eV'))
    # print('-----------------------------------------')
    # print('gamma1')
    # print(GaAs.gamma1)
    # print('-----------------------------------------')
    # print('gamma2')
    # print(GaAs.gamma2)
    # print('-----------------------------------------')
    # print('gamma3')
    # print(GaAs.gamma3)
    # print('-----------------------------------------')
    # print('a_c')
    # print(GaAs.a_c)
    # print(asUnit(GaAs.a_c, 'eV'))
    # print('-----------------------------------------')
    # print('a_v')
    # print(GaAs.a_v)
    # print(asUnit(GaAs.a_v, 'eV'))
    # print('-----------------------------------------')
    # print('b')
    # print(GaAs.b)
    # print(asUnit(GaAs.b, 'eV'))
    # print('-----------------------------------------')
    # print('d')
    # print(GaAs.d)
    # print(asUnit(GaAs.d, 'eV'))
    # print('-----------------------------------------')
    # print('c11')
    # print(GaAs.c11)
    # print(asUnit(GaAs.c11, 'GPa'))
    #
    # print('-----------------------------------------')
    # print('c12')
    # print(GaAs.c12)
    # print(asUnit(GaAs.c12, 'GPa'))
    # print('-----------------------------------------')
    # print('c44')
    # print(GaAs.c44)
    # print(asUnit(GaAs.c44, 'GPa'))
    # print('-----------------------------------------')
    # print('interband_matrix_element')
    # print(GaAs.interband_matrix_element)
    # print(asUnit(GaAs.interband_matrix_element, 'eV'))
    # print('-----------------------------------------')
    # print('spin_orbit_splitting')
    # print(GaAs.spin_orbit_splitting)
    # print(asUnit(GaAs.spin_orbit_splitting, 'eV'))
    #
    # print('-----------------------------------------')
    # print('lattice_constant')
    # print(GaAs.lattice_constant)
    # print('-----------------------------------------')
    # atts.append(GaAs.band_gap)
    # atts.append(GaAs.T)
    # atts.append(GaAs.strained)
    # atts.append(GaAs.valence_band_offset)
    # atts.append(GaAs.eff_mass_electron)
    # atts.append(GaAs.eff_mass_electron_Gamma)
    # atts.append(GaAs.electron_mobility)
    # atts.append(GaAs.hole_mobility)
    # atts.append(GaAs.eff_mass_hh_z)
    # atts.append(GaAs.eff_mass_lh_z)
    # atts.append(GaAs.electron_affinity)
    # atts.append(GaAs.gamma1)
    # atts.append(GaAs.gamma2)
    # atts.append(GaAs.gamma3)
    # atts.append(GaAs.a_c)
    # atts.append(GaAs.a_v)
    # atts.append(GaAs.b)
    # atts.append(GaAs.c11)
    # atts.append(GaAs.c12)
    # atts.append(GaAs.c44)
    # atts.append(GaAs.interband_matrix_element)
    # atts.append(GaAs.spin_orbit_splitting)
    # atts.append(GaAs.lattice_constant)
    # # atts.append(GaAs.electron_minority_lifetime)
    # # atts.append(GaAs.hole_minority_lifetime)
    # # atts.append(GaAs.relative_permittivity)
    # # atts.append(GaAs.electron_auger_recombination)
    # # atts.append(GaAs.hole_auger_recombination)
    # # print(atts)
    # # print('electron_minority_lifetime')
    # # print(GaAs.electron_minority_lifetime)
    # # print('-----------------------------------------')
    # # print('hole_minority_lifetime')
    # # print(GaAs.hole_minority_lifetime)
    # # print('-----------------------------------------')
    # print('relative_permittivity')
    # print(GaAs.relative_permittivity)
    # print('-----------------------------------------')
    # print('electron_auger_recombination')
    # print(GaAs.electron_auger_recombination)
    # print('-----------------------------------------')
    # print('hole_auger_recombination')
    # print(GaAs.hole_auger_recombination)
    # print('-----------------------------------------')
    # # struc = Structure([
    # #     # Layer(width=si(f"10 nm"), material=AlGaAs, role="barrier"),
    # #     Layer(width=si("100 nm"), material=i_GaAs, role="barrier"),
    # #     Layer(width=si(f"10 nm"), material=GaAs, role="well"),  # 5-20 nm
    # #     Layer(width=si("100 nm"), material=i_GaAs, role="barrier"),
    # #     # Layer(width=si(f"100 nm"), material=AlGaAs, role="barrier")
    # # ], substrate=i_GaAs)
    # # SR, bands = QM.schrodinger(struc, num_eigenvalues=20)
    # # schrodinger_graph_LDOS(SR)
    # # plt.show()
    # a, b = QDSC_GaSb_Sw_dotsize()
    # for i in a:
    #     print(i)