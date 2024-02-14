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


MgF2 = material("MgF2")(T=T)
ZnS = material("ZNSCUB", sopra=True)(T=T, )


# Layer(width=si("100 nm"), material=MgF2, role="AR1")
# Layer(width=si("50 nm"), material=ZnS, role="AR2")
# InSb GaSb
def QDSC_InSb_and_GaSb():
    size_InSb = 2.5
    size_GaSb = 20
    AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True)
    n_GaAs = material('GaAs')(T=T, Nd=si('1e18 cm-3'), )
    i_GaAs = material("GaAs")(T=T)
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


def QDSC_InSb_and_GaSb_barrier_mod():
    size_InSb = 2.5
    size_GaSb = 20

    top_barriers = ['AlGaAs', 'n_AlGaAs', 'n_AlInP', "AlInP"]
    bottom_barriers = ['AlGaAs', 'n_AlGaAs', 'n_AlInP', 'AlInP']
    solar_each_function = {}
    for top_barrier in top_barriers:
        for bot_barrier in bottom_barriers:

            AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True)
            n_AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True, Nd=si("3e17 cm-3"),
                                          electron_mobility=si("2000 cm2"), hole_mobility=si("50 cm2"))
            n_GaAs = material('GaAs')(T=T, Nd=si('1e18 cm-3'), )
            n_AlInP = material("AlInP")(T=T, Al=0.42, Nd=si('3e17 cm-3'), electron_mobility=si("400 cm2"),
                                        hole_mobility=si("30 cm2"))
            AlInP = material("AlInP")(T=T, Al=0.42, electron_mobility=si("400 cm2"), hole_mobility=si("30 cm2"))
            i_GaAs = material("GaAs")(T=T)
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
            if top_barrier == "AlGaAs":
                t_barrier = AlGaAs
            elif top_barrier == 'n_AlGaAs':
                t_barrier = n_AlGaAs
            elif top_barrier == 'n_AlInP':
                t_barrier = n_AlInP
            elif top_barrier == "AlInP":
                t_barrier = AlInP

            if top_barrier == "AlGaAs":
                b_barrier = AlGaAs
            elif top_barrier == 'n_AlGaAs':
                b_barrier = n_AlGaAs
            elif top_barrier == 'n_AlInP':
                b_barrier = n_AlInP
            elif top_barrier == "AlInP":
                b_barrier = AlInP

            print(f"top = {top_barrier}, bottom = {bot_barrier}")
            QW = PDD.QWunit([
                                Layer(width=si(f"100 nm"), material=t_barrier, role="barrier"),
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
                            [Layer(width=si(f"100 nm"), material=b_barrier, role="barrier")
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
            solar_each_function[f"top = {top_barrier}, bottom = {bot_barrier}"] = solarcell_InSb_GaSb
    return solar_each_function


# set_solar = QDSC_InSb_and_GaSb_barrier_mod()
#
# for key, cell in set_solar.items():
#     print(key)
#     printstructure(cell)
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


def solar_cell_InSb_and_GaSb_interlayer():
    # compare interlayer i_GaAs is barrier and interlayer
    interlayer = [5, 15, 25, 35, 45]
    size_InSb = 2.5
    size_GaSb = 20
    solar_each_size_1 = {}
    # for i in interlayer:
    tasks = ["interlayer", "barrier", 'spacial']
    i: str
    for i in tasks:
        AlGaAs = material("AlGaAs")(T=T, Al=0.3, strained=True)
        n_GaAs = material('GaAs')(T=T, Nd=si('1e18 cm-3'), )
        i_GaAs = material("GaAs")(T=T, )
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
        if i == "spacial":
            t_b = "barrier"
            mid = "interlayer"
        else:
            mid = i;t_b = i
        # print(InSb.eff_mass_lh_z)
        QW = PDD.QWunit([
                            Layer(width=si(f"100 nm"), material=AlGaAs, role="barrier"),
                        ]
                        +
                        [Layer(width=si(f"{50} nm"), material=i_GaAs, role=t_b),
                         Layer(width=si(f"{size_InSb} nm"), material=InSb, role="well"),  # 5-20 nm
                         Layer(width=si(f"{10} nm"), material=i_GaAs, role=mid),
                         Layer(width=si(f"{size_GaSb} nm"), material=GaSb, role="well"),
                         Layer(width=si(f"{50} nm"), material=i_GaAs, role=t_b),
                         ]  # 5-20 nm
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
        solar_each_size_1[f"i_GaAs in dot is = {i}"] = solarcell_InSb_GaSb
    return solar_each_size_1


# print([i for i in solar_cell_InSb_and_GaSb_interlayer()])
