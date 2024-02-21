import solcore
from solcore import si, material
from solcore.structure import Layer, Structure, Junction, SolcoreMaterialToStr
from solcore.solar_cell import SolarCell
import solcore.quantum_mechanics as QM
import solcore.poisson_drift_diffusion as PDD
from solcore.quantum_mechanics.high_level_kp_QW import schrodinger
from save_picture import schrodinger_graph_LDOS
import numpy as np
import matplotlib.pyplot as plt
from solcore.quantum_mechanics.kp_bulk import KPbands
import pickle

# ==================================================================================================================
# setup
T = 300
wl = np.linspace(350, 1200, 401) * 1e-9

def printstructure(solar_cell):
    space = "+" + '=' * 70 + "+"
    print(space + '\n' + f"\n".join(["{}".format(layer) for layer in solar_cell]) + '\n' + space)
    return str(space + '\n' + f"\n".join(["{}".format(layer) for layer in solar_cell]) + '\n' + space)

def show_QD_graph(list_struc):
    # InSb_no_strain = material("InSb")(T=T)
    # struc = Structure( list_struc ,substrate = p_GaAs, T=T)
    RS, bands = QM.schrodinger(Structure(
        # [Layer(width=si("100 nm"), material=n_GaAs, role="Emitter")]+
        list_struc * 3
        # +[Layer(width=si("100 nm"), material=p_GaAs, role="Emitter"),]
        , substrate=i_GaAs, T=T)
        , quasiconfined=0.01
        , num_eigenvalues=10
        , show=False
        # , graphtype='potentialsLDOS'
        , mode='kp6x6'
    )
    return RS, bands

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

n_GaAs = material('GaAs')(T=T, Nd=si('1e17 cm-3'), )
i_GaAs = material("GaAs")(T=T)
i_GaAs_barrier = material("GaAs")(T=T, strained=True, eff_mass_electron_Gamma=0.067
                                  , eff_mass_hh_z=0.51
                                  , eff_mass_lh_z=0.082)
p_GaAs = material("GaAs")(T=T, Na=si("1e17 cm-3"), )
InSb = material("InSb")(T=T
                        , strained=True
                        , electron_mobility=7.7
                        , hole_mobility=0.0850, valence_band_offset=si("0.0 eV")
                        , band_gap=si("0.173723 eV"), spin_orbit_splitting=si("0.81 eV")
                        , gamma1=34.8, gamma2=15.5, gamma3=16.5
                        , a_c=si("-6.94 eV"), a_v=si("-0.36 eV"), b=si("-2 eV")
                        )
MgF2 = material("MgF2")(T=T)
ZnS = material("ZNSCUB", sopra=True)(T=T, )
# Layer(width=si("100 nm"), material=MgF2, role="AR1")
# Layer(width=si("50 nm"), material=ZnS, role="AR2")

#end setup
# ==================================================================================================================
# material (ref : Electrical and optical properties of InSb/GaAg QDSC for photovoltaic)

def ref_GaAs():
    #define material
    n_GaAs = material('GaAs')(T=T, Nd=si('1e18 cm-3'), )
    p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
    InSb = material("InSb")(T=T
                            , strained=True
                            , electron_mobility=7.7
                            , hole_mobility=0.0850, valence_band_offset=si("0.0 eV")
                            , band_gap=si("0.173723 eV"), spin_orbit_splitting=si("0.81 eV")
                            , gamma1=34.8, gamma2=15.5, gamma3=16.5
                            , a_c=si("-6.94 eV"), a_v=si("-0.36 eV"), b=si("-2 eV")
                            )
    # reference :https://www.ioffe.ru/SVA/NSM/Semicond/InSb/basic.html (electron_affinity)
    # reference :https://www.ioffe.ru/SVA/NSM/Semicond/InSb/electric.html
    #========================================================================================================
    #combine material
    QW = PDD.QWunit([
        Layer(width=si("20 nm"), material=i_GaAs, role="barrier"),
        Layer(width=si("2.54 nm"), material=InSb, role="well"),  # 5-20 nm
        Layer(width=si("20 nm"), material=i_GaAs, role="barrier"),
    ], T=T, repeat=5, substrate=i_GaAs, )
    QW_list = QW.GetEffectiveQW(wavelengths=wl)
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
    return my_solar_cell
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
    #define material
    n_GaAs = material('GaAs')(T=T, Nd=si('1e18 cm-3'), )
    p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
    n_GaAs_barrier = material('GaAs')(T=T, Nd=si('1e17 cm-3'),strained=True )
    i_GaAs_barrier = material("GaAs")(T=T, strained=True)
    InSb1 = material("InSb")(T=T
                            , strained=True
                            , valance_band_offset=si("0.0 eV")
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
                            , electron_auger_recombination=si("5e-26 cm6")
                            , hole_auger_recombination=si("5e-26 cm6")
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
        Layer(width=si("50 nm"), material=n_GaAs_barrier, role="barrier"),
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
def dot_InSb_reference():
    #define material
    n_GaAs = material('GaAs')(T=T, Nd=si('1e18 cm-3'), )
    p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
    n_GaAs_barrier = material('GaAs')(T=T, Nd=si('1e17 cm-3'),strained=True )
    i_GaAs_barrier = material("GaAs")(T=T, strained=True)
    InSb1 = material("InSb")(T=T
                            , strained=True
                            , valance_band_offset=si("0.0 eV")
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
                            , electron_auger_recombination=si("5e-26 cm6")
                            , hole_auger_recombination=si("5e-26 cm6")
                            )
    InSb = material("InSb")(T=T, strained=True)
    # reference :https://www.ioffe.ru/SVA/NSM/Semicond/InSb/basic.html (electron_affinity)
    # reference :https://www.ioffe.ru/SVA/NSM/Semicond/InSb/electric.html
    #========================================================================================================
    #combine material
    QW = PDD.QWunit([
        Layer(width=si("100 nm"), material=i_GaAs_barrier, role="barrier"),
        Layer(width=si("1 nm"), material=InSb1, role="well"),  # 5-20 nm
        Layer(width=si("50 nm"), material=n_GaAs_barrier, role="barrier"),
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
    dot_size = np.linspace(100, 500, 10)
    # modes = ['kp8x8_bulk']
    print(dot_size)
    plot_note = dict(x_axis=dot_size, x_axis_name="n_Layer between dot and p(nm)")
    solar_each_size_1 = {}
    for dot in dot_size:
        # define material
        # AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True, Nd=si("1e17 cm-3"))
        n_GaAs = material('GaAs')(T=T, Nd=si('1e17 cm-3'), )
        i_GaAs = material("GaAs")(T=T)
        i_GaAs_barrier = material("GaAs")(T=T, strained=True, eff_mass_electron_Gamma=0.067
                                          , eff_mass_hh_z=0.51
                                          , eff_mass_lh_z=0.082)
        n_GaAs_barrier = material("GaAs")(T=T, strained=True, eff_mass_electron_Gamma=0.067
                                          , eff_mass_hh_z=0.51
                                          , eff_mass_lh_z=0.082, Nd=si('1e17 cm-3'))
        p_GaAs = material("GaAs")(T=T, Na=si("1e17 cm-3"), )
        InSb = material("InSb")(T=T
                                , strained=True
                                , electron_mobility=7.8
                                , hole_mobility=0.0850
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
        QW_list = QW.GetEffectiveQW(wavelengths=wl, use_Adachi=True)
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
        solar_each_size_1[f"n layer = {dot}nm"] = my_solar_cell
    return solar_each_size_1, plot_note
def dot_InSb_n_top_sweep():
    # define setup
    dot_size = np.linspace(50, 500, 10)
    # modes = ['kp8x8_bulk']
    print(dot_size)
    plot_note = dict(x_axis=dot_size, x_axis_name="top layer (nm)")
    solar_each_size_1 = {}
    for dot in dot_size:
        # define material
        # AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True, Nd=si("1e17 cm-3"))
        n_GaAs = material('GaAs')(T=T, Nd=si('1e17 cm-3'), )
        i_GaAs = material("GaAs")(T=T)
        i_GaAs_barrier = material("GaAs")(T=T, strained=True, eff_mass_electron_Gamma=0.067
                                          , eff_mass_hh_z=0.51
                                          , eff_mass_lh_z=0.082)
        n_GaAs_barrier = material("GaAs")(T=T, strained=True, eff_mass_electron_Gamma=0.067
                                          , eff_mass_hh_z=0.51
                                          , eff_mass_lh_z=0.082, Nd=si('1e17 cm-3'))
        p_GaAs = material("GaAs")(T=T, Na=si("1e17 cm-3"), )
        InSb = material("InSb")(T=T
                                , strained=True
                                , electron_mobility=7.8
                                , hole_mobility=0.0850
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
        QW_list = QW.GetEffectiveQW(wavelengths=wl, use_Adachi=True)
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
        solar_each_size_1[f"n layer = {dot}nm"] = my_solar_cell
    return solar_each_size_1, plot_note

def dot_InSb_n_inter_sweep():
    # define setup
    dot_size = np.linspace(10, 300, 10)
    # modes = ['kp8x8_bulk']
    print(dot_size)
    plot_note = dict(x_axis=dot_size, x_axis_name="inter layer (nm)")
    solar_each_size_1 = {}
    for dot in dot_size:
        print(dot)
        # define material
        # AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True, Nd=si("1e17 cm-3"))
        n_GaAs = material('GaAs')(T=T, Nd=si('1e17 cm-3'), )
        i_GaAs = material("GaAs")(T=T)
        i_GaAs_barrier = material("GaAs")(T=T, strained=True, eff_mass_electron_Gamma=0.067
                                          , eff_mass_hh_z=0.51
                                          , eff_mass_lh_z=0.082)
        n_GaAs_barrier = material("GaAs")(T=T, strained=True, eff_mass_electron_Gamma=0.067
                                          , eff_mass_hh_z=0.51
                                          , eff_mass_lh_z=0.082, Nd=si('1e17 cm-3'))
        p_GaAs = material("GaAs")(T=T, Na=si("1e17 cm-3"), )
        InSb = material("InSb")(T=T
                                , strained=True
                                , electron_mobility=7.8
                                , hole_mobility=0.0850
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
        QW_list = QW.GetEffectiveQW(wavelengths=wl, use_Adachi=True)
        GaAs_junction = Junction([
                                     Layer(width=si("350 nm"), material=n_GaAs, role="Emitter"),
                                 ]
                                 + QW_list
                                 + [
                                     Layer(width=si(f"250 nm"), material=n_GaAs, role="Emitter"),
                                     Layer(width=si("1700 nm"), material=p_GaAs, role="Emitter"),
                                 ],
                                 T=T, kind="PDD", substrate=p_GaAs)
        my_solar_cell = SolarCell([
            GaAs_junction,
        ]
            , T=T, substrate=p_GaAs)
        solar_each_size_1[f"n layer = {dot}nm"] = my_solar_cell
    return solar_each_size_1, plot_note
# dot_InSb_n_inter_sweep()
def InSb_dot_size():
    # define setup
    dot_size = np.linspace(0.1, 3, 31)
    # modes = ['kp8x8_bulk']
    print(dot_size)
    plot_note = dict(x_axis=dot_size, x_axis_name="Dot size(nm)")
    solar_each_size_1 = {}
    for dot in dot_size:
        # define material
        # AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True, Nd=si("1e17 cm-3"))
        n_GaAs = material('GaAs')(T=T, Nd=si('1e17 cm-3'), )
        i_GaAs = material("GaAs")(T=T)
        i_GaAs_barrier = material("GaAs")(T=T, strained=True, eff_mass_electron_Gamma=0.067
                                          , eff_mass_hh_z=0.51
                                          , eff_mass_lh_z=0.082)
        n_GaAs_barrier = material("GaAs")(T=T, strained=True, eff_mass_electron_Gamma=0.067
                                          , eff_mass_hh_z=0.51
                                          , eff_mass_lh_z=0.082, Nd=si('1e17 cm-3'))
        p_GaAs = material("GaAs")(T=T, Na=si("1e17 cm-3"), )
        InSb = material("InSb")(T=T
                                , strained=True
                                , electron_mobility=7.8
                                , hole_mobility=0.0850
                                )
        GaSb = material("GaSb")(T=T, strained=True, )
        # =============================================================================================
        # combine material
        QW = PDD.QWunit([
            # Layer(width=si(f"15 nm"), material=AlGaAs, role="barrier"),
            Layer(width=si("100 nm"), material=i_GaAs_barrier, role="barrier"),
            Layer(width=si(f"{dot} nm"), material=InSb, role="well"),  # 5-20 nm
            Layer(width=si("100 nm"), material=n_GaAs_barrier, role="barrier"),
            # Layer(width=si(f"15 nm"), material=AlGaAs, role="barrier")
        ], T=T, repeat=1, substrate=i_GaAs)
        QW_list = QW.GetEffectiveQW(wavelengths=wl, use_Adachi=True)
        GaAs_junction = Junction([
                                     Layer(width=si("350 nm"), material=n_GaAs, role="Emitter"),
                                 ]
                                 + QW_list
                                 + [
                                     Layer(width=si("200 nm"), material=n_GaAs, role="Emitter"),
                                     Layer(width=si("1700 nm"), material=p_GaAs, role="Emitter"),
                                 ],
                                 T=T, kind="PDD", substrate=p_GaAs)
        my_solar_cell = SolarCell([
            GaAs_junction,
        ]
            , T=T, substrate=p_GaAs)
        solar_each_size_1[f"dot size ={dot} nm"] = my_solar_cell
    return solar_each_size_1, plot_note

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
        n_GaAs = material('GaAs')(T=T, Nd=si('1e17 cm-3'), )
        i_GaAs = material("GaAs")(T=T)
        i_GaAs_barrier = material("GaAs")(T=T, strained=True, eff_mass_electron_Gamma=0.067
                                          , eff_mass_hh_z=0.51
                                          , eff_mass_lh_z=0.082)
        p_GaAs = material("GaAs")(T=T, Na=si("1e17 cm-3"), )
        InSb = material("InSb")(T=T
                                , strained=True
                                , electron_mobility=7.7
                                , hole_mobility=0.0850, valence_band_offset=si("0.0 eV")
                                , band_gap=si("0.173723 eV"), spin_orbit_splitting=si("0.81 eV")
                                , gamma1=34.8, gamma2=15.5, gamma3=16.5
                                , a_c=si("-6.94 eV"), a_v=si("-0.36 eV"), b=si("-2 eV")
                                )
        GaSb = material("GaSb")(T=T, strained=True, )
        # =============================================================================================
        # combine material
        QW = PDD.QWunit([
            Layer(width=si(f"100 nm"), material=AlGaAs, role="barrier"),
            Layer(width=si("100 nm"), material=i_GaAs_barrier, role="barrier"),
            Layer(width=si(f"{dot} nm"), material=InSb, role="well"),  # 5-20 nm
            Layer(width=si("50 nm"), material=n_GaAs, role="barrier"),
            Layer(width=si(f"100 nm"), material=AlGaAs, role="barrier")
        ], T=T, repeat=1, substrate=i_GaAs)
        QW_list = QW.GetEffectiveQW(wavelengths=wl, use_Adachi=True)
        GaAs_junction = Junction([
                                     Layer(width=si("50 nm"), material=n_GaAs, role="Emitter"),
                                 ]
                                 + QW_list
                                 + [
                                     Layer(width=si("100 nm"), material=n_GaAs, role="Emitter"),
                                     Layer(width=si("1700 nm"), material=p_GaAs, role="Emitter"),
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

    solar_each_size_1 = {}
    for dot in dot_size:
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
            Layer(width=si(f"15 nm"), material=AlGaAs, role="barrier"),
            Layer(width=si("10 nm"), material=i_GaAs_barrier, role="interlayer"),
            Layer(width=si(f"{dot} nm"), material=GaSb, role="well"),  # 5-20 nm
            Layer(width=si("10 nm"), material=i_GaAs_barrier, role="interlayer"),
            Layer(width=si(f"15 nm"), material=AlGaAs, role="barrier")
        ], T=T, repeat=5, substrate=i_GaAs)
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
        solar_each_size_1[f"InSb size ={dot} nm"] = my_solar_cell
        return solar_each_size_1

#===========================================================================================================

def QDSC_InAs_GaSb():
    size_InAs = 11
    size_GaSb = 15
    AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True)
    n_GaAs = material('GaAs')(T=T, Nd=si('1e18 cm-3'), )
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
    InAs = material("INAS", sopra=True)(T=T, strained=True,
                                        valence_band_offset=si("-0.59 eV"),
                                        band_gap=si("0.417 eV"),
                                        eff_mass_electron=0.023,
                                        eff_mass_electron_Gamma=0.026,
                                        electron_mobility=si("3.5e4 cm2"),
                                        hole_mobility=si("5e2 cm2"),
                                        eff_mass_hh_z=0.64,
                                        eff_mass_lh_z=0.05,
                                        electron_affinity=si("4.9 eV"),
                                        gamma1=20, gamma2=8.5, gamma3=9.2,
                                        a_c=si("-5.08 eV"), a_v=si("-1 eV"), b=si("-1.8 eV"), d=si("-3.6 eV"),
                                        c11=si("832.9 GPa"), c12=si("452.6 GPa"), c44=si("395.9 GPa"),
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
    # print(InSb.eff_mass_lh_z)
    solar_each_size_1 = {}
    interlayer = [5, 10, 15, 20, 25]
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
    # solar_each_size_1[f"dot stack ={stack}"] = solarcell_InAs_GaSb
    return solarcell_InAs_GaSb

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

