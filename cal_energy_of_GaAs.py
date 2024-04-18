import numpy as np
#for AlGaAs
Ec = 0.7228
Ec_error = 0.02
Ev = -0.766
#for GaAs
# Ec = 0.623
# Ec_error = 0.02
# Ev = -0.8
def cal_wl_form_ev(state):
    print(f"top wave upper bound is {1240/(np.abs(Ec-state)+Ec_error)} nm")
    print(f"top wave is {1240/(np.abs(Ec-state))} nm")
    print(f"top wave lower bound is {1240/(np.abs(Ec-state)-Ec_error)} nm")

    # print(f"bottom wave upper bound is {1240/(np.abs(Ev-state))} nm")
    print(f"bottom wave is {1240/(np.abs(Ev-state))} nm")
    # print(f"bottom wave lower bound is {1240/(np.abs(Ev-state))} nm")

i = input("insert your state: ")
while(True):
    try:
        state = float(i)
    except:
        exit
    cal_wl_form_ev(state)
    i = input("insert your state: ")