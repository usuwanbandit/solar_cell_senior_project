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

def QDSC_InSb():
    #define material
    n_GaAs = material('GaAs')(T=T, Nd=si('1e17 cm-3'), )
    i_GaAs = material("GaAs")(T=T, strained=True, band_gap=si("1.422 eV"))
    p_GaAs = material("GaAs")(T=T, Na=si("1e17 cm-3"), )
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
                                 Layer(width=si("230 nm"), material=n_GaAs, role="Emitter"),
                             ]
                             # +QW_list
                             + [
                                 Layer(width=si("1700 nm"), material=p_GaAs, role="Emitter"),
                             ],
                             T=T, kind="PDD", )
    my_solar_cell = SolarCell([
        Layer(width=si("100 nm"), material=MgF2, role="AR1"),
        Layer(width=si("50 nm"), material=ZnS, role="AR2"),
        GaAs_junction,
    ]
        , T=T, substrate=p_GaAs)

    return my_solar_cell
#===========================================================================================================

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
        solar_each_size_1[f"dot size ={dot}"] = my_solar_cell
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
                                        electron_auger_recombination=si("15e-30 cm6"),
                                        hole_auger_recombination=si("15e-31 cm6"),
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

def QDSC_InAs_GaSb_sweep_interlayer():
    playload_solar_cell = {}
    interlayer = [5, 10, 15, 20, 25]
    for i in interlayer:
        size_InAs = 11
        size_GaSb = 15
        AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True)
        n_GaAs = material('GaAs')(T=T, Nd=si('1e18 cm-3'), )
        i_GaAs = material("GaAs")(T=T)

        p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
        p_GaInP = material("GaInP")(T=T, In=0.42, Na=si("2e18 cm-3"))
        p_GaAs_buffer = material("GaAs")(T=T, Na=si("2e18 cm-3"))
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
                                            electron_auger_recombination=si("15e-30 cm6"),
                                            hole_auger_recombination=si("15e-31 cm6"),
                                            )

        GaSb = material("GaSb")(T=T, strained=True,
                                electron_mobility=si("3e3 cm2"),
                                hole_mobility=si("1e3 cm2"),
                                )
        # print(InSb.eff_mass_lh_z)
        print(i)
        QW = PDD.QWunit([
                            Layer(width=si(f"100 nm"), material=AlGaAs, role="barrier"),
                        ]
                        +
                        [Layer(width=si(f"50 nm"), material=i_GaAs, role="barrier"),
                         Layer(width=si(f"{size_GaSb} nm"), material=GaSb, role="well"),  # 5-20 nm
                         Layer(width=si(f"{i} nm"), material=i_GaAs, role="barrier"),
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
        buffer_solar_cell = SolarCell([
            Layer(width=si("100 nm"), material=MgF2, role="AR1"),
            Layer(width=si("50 nm"), material=ZnS, role="AR2"),
            GaAs_junction,
        ]
            , T=T, substrate=p_GaAs)
        playload_solar_cell[f"interlayer width = {i}nm"] = buffer_solar_cell
    return playload_solar_cell


def QDSC_InAs_GaSb_sweep_stack():
    playload_solar_cell = {}
    stack = [5, 4, 3, 2, 1]
    for i in stack:
        size_InAs = 11
        size_GaSb = 15
        AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True)
        n_GaAs = material('GaAs')(T=T, Nd=si('1e18 cm-3'), )
        i_GaAs = material("GaAs")(T=T)

        p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
        p_GaInP = material("GaInP")(T=T, In=0.42, Na=si("2e18 cm-3"))
        p_GaAs_buffer = material("GaAs")(T=T, Na=si("2e18 cm-3"))
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
                                            electron_auger_recombination=si("15e-30 cm6"),
                                            hole_auger_recombination=si("15e-31 cm6"),
                                            )
        GaSb = material("GaSb")(T=T, strained=True,
                                electron_mobility=si("3e3 cm2"),
                                hole_mobility=si("1e3 cm2"),
                                )
        # print(InSb.eff_mass_lh_z)
        print(i)
        QW = PDD.QWunit([
                            # Layer(width=si(f"100 nm"), material=AlGaAs, role="barrier"),
                        ]
                        +
                        [Layer(width=si(f"50 nm"), material=i_GaAs, role="barrier"),
                         Layer(width=si(f"{size_GaSb} nm"), material=GaSb, role="well"),  # 5-20 nm
                         Layer(width=si("5 nm"), material=i_GaAs, role="barrier"),
                         Layer(width=si(f"{size_InAs} nm"), material=InAs, role="well"),  # 5-20 nm
                         Layer(width=si("200 nm"), material=i_GaAs, role="barrier"), ] * i

                        # Layer(width=si("20 nm"), material=i_GaAs, role="barrier"),]*dot
                        +
                        [
                            # Layer(width=si(f"100 nm"), material=AlGaAs, role="barrier")
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
        buffer_solar_cell = SolarCell([
            Layer(width=si("100 nm"), material=MgF2, role="AR1"),
            Layer(width=si("50 nm"), material=ZnS, role="AR2"),
            GaAs_junction,
        ]
            , T=T, substrate=p_GaAs)
        playload_solar_cell[f"stack = {i}"] = buffer_solar_cell
    return playload_solar_cell


# ===============================================================
# InSb GaSb
def solar_cell_InSb_and_GaSb():
    interlayer = [5, 15, 25, 35, 45]
    size_InSb = 2.5
    size_GaSb = 20
    # solar_each_size_1 = {}
    # for i in interlayer:
    AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True)
    n_GaAs = material('GaAs')(T=T, Nd=si('1e18 cm-3'), )
    i_GaAs = material("GaAs")(T=T)
    # p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
    p_GaInP = material("GaInP")(T=T, In=0.42, Na=si("2e18 cm-3"))
    p_GaAs_buffer = material("GaAs")(T=T, Na=si("2e18 cm-3"))

    p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
    InSb = material("InSb")(T=T
                            , strained=False
                            , electron_mobility=7.7
                            , hole_mobility=0.0850, valence_band_offset=si("0.0 eV")
                            , band_gap=si("0.173723 eV"), spin_orbit_splitting=si("0.81 eV")
                            , gamma1=34.8, gamma2=15.5, gamma3=16.5
                            , a_c=si("-6.94 eV"), a_v=si("-0.36 eV"), b=si("-2 eV")
                            )
    GaSb = material("GaSb")(T=T, strained=True,
                            electron_mobility=si("3e3 cm2"),
                            hole_mobility=si("1e3 cm2"),
                            )
    # print(InSb.eff_mass_lh_z)
    QW = PDD.QWunit([
                        Layer(width=si(f"100 nm"), material=AlGaAs, role="barrier"),
                    ]
                    +
                    [Layer(width=si(f"{50} nm"), material=i_GaAs, role="interlayer"),
                     Layer(width=si(f"{size_InSb} nm"), material=InSb, role="well"),  # 5-20 nm
                     Layer(width=si(f"{10} nm"), material=i_GaAs, role="interlayer"),
                     Layer(width=si(f"{size_GaSb} nm"), material=GaSb, role="well"),
                     Layer(width=si(f"{50} nm"), material=i_GaAs, role="interlayer"),
                     ]  # 5-20 nm
                    # Layer(width=si("20 nm"), material=i_GaAs, role="barrier"),]*dot

                    +
                    [Layer(width=si(f"100 nm"), material=AlGaAs, role="barrier")
                     ], T=T, repeat=1, substrate=i_GaAs)
    QW_list = QW.GetEffectiveQW(wavelengths=wl, use_Adachi=True)
    GaAs_junction = Junction([
                                 Layer(width=si("130 nm"), material=n_GaAs, role="Emitter"), ]
                             + QW_list
                             + [
                                 Layer(width=si("100 nm"), material=n_GaAs, role="Emitter"),
                                 Layer(width=si("2800 nm"), material=p_GaAs, role="Base"),
                                 Layer(width=si("100 nm"), material=p_GaInP, role="BSF"),
                                 Layer(width=si("150 nm"), material=p_GaAs_buffer, role="Buffer"),
                             ],
                             T=T, kind="PDD", substrate=p_GaAs)
    solarcell_InSb_GaSb = SolarCell([
        Layer(width=si("100 nm"), material=MgF2, role="AR1"),
        Layer(width=si("50 nm"), material=ZnS, role="AR2"),
        GaAs_junction,
    ]
        , T=T, substrate=p_GaAs)
    # solar_each_size_1[f"interlayer ={i}"] = solarcell_InSb_GaSb
    return solarcell_InSb_GaSb


def solar_cell_InSb_and_GaSb_doped():
    interlayer = [5, 15, 25, 35, 45]
    size_InSb = 2.5
    size_GaSb = 20
    # solar_each_size_1 = {}
    # for i in interlayer:
    n_AlInP = material("AlInP")(T=T, Al=0.42, Nd=si('3e17 cm-3'), electron_mobility=si("4000 cm2"))
    AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True)
    n_GaAs = material('GaAs')(T=T, Nd=si('1e18 cm-3'), )
    GaAs_inter = material("GaAs")(T=T, Nd=si('1e14 cm-3'))
    i_GaAs = material("GaAs")(T=T, )
    # p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
    p_GaInP = material("GaInP")(T=T, In=0.42, Na=si("2e18 cm-3"))
    p_GaAs_buffer = material("GaAs")(T=T, Na=si("2e18 cm-3"))

    p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
    InSb = material("InSb")(T=T
                            , strained=True
                            , electron_mobility=7.7
                            , hole_mobility=0.0850, valence_band_offset=si("0.0 eV")
                            , band_gap=si("0.173723 eV"), spin_orbit_splitting=si("0.81 eV")
                            , gamma1=34.8, gamma2=15.5, gamma3=16.5
                            , a_c=si("-6.94 eV"), a_v=si("-0.36 eV"), b=si("-2 eV")
                            )
    GaSb = material("GaSb")(T=T, strained=True,
                            electron_mobility=si("3e3 cm2"),
                            hole_mobility=si("1e3 cm2"),
                            )
    # print(InSb.eff_mass_lh_z)
    QW = PDD.QWunit([
                        Layer(width=si(f"100 nm"), material=AlGaAs, role="barrier"),
                    ]
                    +
                    [Layer(width=si(f"{50} nm"), material=i_GaAs, role="interlayer"),
                     Layer(width=si(f"{size_InSb} nm"), material=InSb, role="well"),  # 5-20 nm
                     Layer(width=si(f"{10} nm"), material=i_GaAs, role="interlayer"),
                     Layer(width=si(f"{size_GaSb} nm"), material=GaSb, role="well"),
                     Layer(width=si(f"{50} nm"), material=i_GaAs, role="interlayer"),
                     ]  # 5-20 nm
                    # Layer(width=si("20 nm"), material=i_GaAs, role="barrier"),]*dot

                    +
                    [Layer(width=si(f"100 nm"), material=AlGaAs, role="barrier")
                     ], T=T, repeat=1, substrate=i_GaAs)
    QW_list = QW.GetEffectiveQW(wavelengths=wl, use_Adachi=True)
    GaAs_junction = Junction([
                                 Layer(width=si("230 nm"), material=n_GaAs, role="Emitter"),
                             ]
                             + QW_list
                             + [
                                 Layer(width=si("100 nm"), material=n_GaAs, role="Emitter"),
                                 Layer(width=si("2800 nm"), material=p_GaAs, role="Base"),
                                 Layer(width=si("100 nm"), material=p_GaInP, role="BSF"),
                                 Layer(width=si("150 nm"), material=p_GaAs_buffer, role="Buffer"),
                             ],
                             T=T, kind="PDD", substrate=p_GaAs)
    solarcell_InSb_GaSb = SolarCell([
        Layer(width=si("100 nm"), material=MgF2, role="AR1"),
        Layer(width=si("50 nm"), material=ZnS, role="AR2"),
        GaAs_junction,
    ]
        , T=T, substrate=p_GaAs)
    # solar_each_size_1[f"interlayer ={i}"] = solarcell_InSb_GaSb
    return solarcell_InSb_GaSb


def solar_cell_InSb_and_GaSb_sweep_interlayer():
    interlayer = [1, 2, 3, 4, 5]
    size_InSb = 2.5
    size_GaSb = 20
    solar_each_size_1 = {}
    for i in interlayer:
        AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True)
        n_GaAs = material('GaAs')(T=T, Nd=si('1e18 cm-3'), )
        i_GaAs = material("GaAs")(T=T)
        # p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
        p_GaInP = material("GaInP")(T=T, In=0.42, Na=si("2e18 cm-3"))
        p_GaAs_buffer = material("GaAs")(T=T, Na=si("2e18 cm-3"))

        p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
        InSb = material("InSb")(T=T
                                , strained=True
                                , electron_mobility=7.7
                                , hole_mobility=0.0850, valence_band_offset=si("0.0 eV")
                                , band_gap=si("0.173723 eV"), spin_orbit_splitting=si("0.81 eV")
                                , gamma1=34.8, gamma2=15.5, gamma3=16.5
                                , a_c=si("-6.94 eV"), a_v=si("-0.36 eV"), b=si("-2 eV")
                                )
        GaSb = material("GaSb")(T=T, strained=True,
                                electron_mobility=si("3e3 cm2"),
                                hole_mobility=si("1e3 cm2"),
                                )
        # print(InSb.eff_mass_lh_z)
        QW = PDD.QWunit([
                            Layer(width=si(f"100 nm"), material=AlGaAs, role="barrier"),
                        ]
                        +
                        [Layer(width=si(f"{50} nm"), material=i_GaAs, role="interlayer"),
                         Layer(width=si(f"{size_InSb} nm"), material=InSb, role="well"),  # 5-20 nm
                         Layer(width=si(f"{5} nm"), material=i_GaAs, role="interlayer"),
                         Layer(width=si(f"{size_GaSb} nm"), material=GaSb, role="well"), ] * i  # 5-20 nm
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
        solarcell_InSb_GaSb = SolarCell([
            Layer(width=si("100 nm"), material=MgF2, role="AR1"),
            Layer(width=si("50 nm"), material=ZnS, role="AR2"),
            GaAs_junction,
        ]
            , T=T, substrate=p_GaAs)
        solar_each_size_1[f"stack  ={i}"] = solarcell_InSb_GaSb
    return solar_each_size_1


def solar_cell_InSb_and_GaSb_sweep_n():
    interlayer = [100, 140, 180, 220]
    size_InSb = 2.5
    size_GaSb = 20
    solar_each_size_1 = {}
    for i in interlayer:
        AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True)
        n_GaAs = material('GaAs')(T=T, Nd=si('1e18 cm-3'), )
        i_GaAs = material("GaAs")(T=T)
        # p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
        p_GaInP = material("GaInP")(T=T, In=0.42, Na=si("2e18 cm-3"))
        p_GaAs_buffer = material("GaAs")(T=T, Na=si("2e18 cm-3"))

        p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
        InSb = material("InSb")(T=T
                                , strained=True
                                , electron_mobility=7.7
                                , hole_mobility=0.0850, valence_band_offset=si("0.0 eV")
                                , band_gap=si("0.173723 eV"), spin_orbit_splitting=si("0.81 eV")
                                , gamma1=34.8, gamma2=15.5, gamma3=16.5
                                , a_c=si("-6.94 eV"), a_v=si("-0.36 eV"), b=si("-2 eV")
                                )
        GaSb = material("GaSb")(T=T, strained=True,
                                electron_mobility=si("3e3 cm2"),
                                hole_mobility=si("1e3 cm2"),
                                )
        # print(InSb.eff_mass_lh_z)
        QW = PDD.QWunit([
                            Layer(width=si(f"100 nm"), material=AlGaAs, role="barrier"),
                        ]
                        +
                        [Layer(width=si(f"{50} nm"), material=i_GaAs, role="interlayer"),
                         Layer(width=si(f"{size_InSb} nm"), material=InSb, role="well"),  # 5-20 nm
                         Layer(width=si(f"{5} nm"), material=i_GaAs, role="interlayer"),
                         Layer(width=si(f"{size_GaSb} nm"), material=GaSb, role="well"), ]  # 5-20 nm
                        # Layer(width=si("20 nm"), material=i_GaAs, role="barrier"),]*dot

                        +
                        [Layer(width=si(f"100 nm"), material=AlGaAs, role="barrier")
                         ], T=T, repeat=1, substrate=i_GaAs)
        QW_list = QW.GetEffectiveQW(wavelengths=wl, use_Adachi=True)
        GaAs_junction = Junction([
                                     Layer(width=si(f"{i} nm"), material=n_GaAs, role="Emitter"), ]
                                 + QW_list
                                 + [
                                     Layer(width=si("100 nm"), material=n_GaAs, role="Emitter"),
                                     Layer(width=si("2800 nm"), material=p_GaAs, role="Base"),
                                     Layer(width=si("100 nm"), material=p_GaInP, role="BSF"),
                                     Layer(width=si("150 nm"), material=p_GaAs_buffer, role="Buffer"),
                                 ],
                                 T=T, kind="PDD", substrate=p_GaAs)
        solarcell_InSb_GaSb = SolarCell([
            Layer(width=si("100 nm"), material=MgF2, role="AR1"),
            Layer(width=si("50 nm"), material=ZnS, role="AR2"),
            GaAs_junction,
        ]
            , T=T, substrate=p_GaAs)
        solar_each_size_1[f"n width  ={i}"] = solarcell_InSb_GaSb
    return solar_each_size_1

# ===============================================================
# solar_cell_InSb_and_GaSb_window()
# a = [1, 3, 4 , 'sddsa']
# b = [str(i) for i in a]
# print(b)
# with open('test.txt', "w") as fin:


# # yoyo = solar_cell_InSb_and_GaSb_sweep_interlayer()
# # yoyo = solar_cell_InSb_and_GaSb()
# size_InSb = 2.5
# size_GaSb = 20
# # solar_each_size_1 = {}
# # for i in interlayer:
# AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True)
# n_GaAs = material('GaAs')(T=T, Nd=si('1e18 cm-3'), )
# i_GaAs = material("GaAs")(T=T)
# # p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
# p_GaInP = material("GaInP")(T=T, In=0.42, Na=si("2e18 cm-3"))
# p_GaAs_buffer = material("GaAs")(T=T, Na=si("2e18 cm-3"))
#
# p_GaAs = material("GaAs")(T=T, Na=si("1e16 cm-3"), )
# InSb = material("InSb")(T=T
#                         , strained=True
#                         , electron_mobility=7.7
#                         , hole_mobility=0.0850, valence_band_offset=si("0.0 eV")
#                         , band_gap=si("0.173723 eV"), spin_orbit_splitting=si("0.81 eV")
#                         , gamma1=34.8, gamma2=15.5, gamma3=16.5
#                         , a_c=si("-6.94 eV"), a_v=si("-0.36 eV"), b=si("-2 eV")
#                         )
# GaSb = material("GaSb")(T=T, strained=True,
#                         electron_mobility=si("3e3 cm2"),
#                         hole_mobility=si("1e3 cm2"),
#                         )
# solar = Structure(
#     [
#         Layer(width=si("330 nm"), material=n_GaAs, role="Emitter"),
#     ]
#     +
#     [
#         Layer(width=si(f"100 nm"), material=AlGaAs, role="barrier"),
#         ]
#         +
#         [Layer(width=si(f"{50} nm"), material=i_GaAs, role="interlayer"),
#         Layer(width=si(f"{size_InSb} nm"), material=InSb, role="well"), # 5-20 nm
#         Layer(width=si(f"{50} nm"), material=i_GaAs, role="interlayer"),
#         Layer(width=si(f"{size_GaSb} nm"), material=GaSb, role="well"),
#     ]  # 5-20 nm
#     +
#     [
#         Layer(width=si(f"100 nm"), material=AlGaAs, role="barrier")
#     ]
#     +
#     [
#         # Layer(width=si("100 nm"), material=n_GaAs, role="Emitter"),
#         Layer(width=si("2800 nm"), material=p_GaAs, role="Base"),
#         Layer(width=si("100 nm"), material=p_GaInP, role="BSF"),
#         Layer(width=si("150 nm"), material=p_GaAs_buffer, role="Buffer"),
#     ],substrate=p_GaAs)
#
# SR, bands = schrodinger(solar, num_eigenvalues=100)
# schrodinger_graph_LDOS(SR)
# plt.show()
# print([str(i) for i in yoyo])
# solar_cell_InAs_GaSb_sweep_stack()
# solar_cell_typeI_and_II()
# solar_cell_InAs_GaSb()
# solar_cell_InAs_GaSb()
# for i in solarcell_InSb_GaSb:
#     print(i)


#
# import os
# from solcore.config_tools import add_source
#
# home_folder = os.path.expanduser('~')
# custom_nk_path = os.path.join(home_folder, 'Solcore/custommats')
# nk_db_path = os.path.join(home_folder, 'Solcore/NK.db')
# param_path = os.path.join(home_folder, 'Solcore/custom_params.txt')
#
# add_source('Others', 'custom_mats', custom_nk_path)
# add_source('Others', 'nk', nk_db_path)
# add_source('Parameters', 'custom', param_path)
