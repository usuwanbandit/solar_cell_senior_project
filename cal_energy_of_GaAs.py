import numpy as np
Ec = 0.624
Ev = -0.8

def cal_wl_form_ev(state):
    print(f"top wave is {1240/(np.abs(Ev-state))} nm")
    print(f"bottom wave is {1240/(np.abs(state-Ec))} nm")

i = input("insert your state: ")
while(True):
    try:
        state = float(i)
    except:
        exit
    cal_wl_form_ev(state)
    i = input("insert your state: ")