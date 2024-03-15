import solcore
from solcore.material_data.mobility import calculate_AlGaAs, mobility_low_field, calculate_mobility
from solcore import material
import numpy as np
import matplotlib.pyplot as plt
from solcore.absorption_calculator.sopra_db import sopra_database
def task1():
    # Composition parameter for Al0.3Ga0.7As
    x = 0.3

    # Carrier type (n for electrons, p for holes)
    carrier_type = 2  # Calculate electron mobility

    # Temperature in Kelvin
    temperature = 300  # Example temperature

    # Calculate the carrier mobility
    mobility = solcore.material_data.mobility.calculate_AlGaAs(x, carrier_type, temperature)

    # Print the result
    print("Carrier mobility for Al0.3Ga0.7As ({}-type) at {} K: {} cm^2/Vs".format(carrier_type, temperature, mobility))
def task2():

    T = 300
    mat1 = material('InAsSb')(Sb=1, T=T, strained=True)
    carrier_type = 0
    mobility = calculate_mobility(mat1,0, 0,0,T)
    wl = np.linspace(350, 1800, 500) * 1e-9
    print("Carrier mobility for Al0.3Ga0.7As ({}-type) at {} K: {} cm^2/Vs".format(carrier_type, T, mobility))
    a = solcore.absorption_calculator.adachi_alpha.create_adachi_alpha(mat1, Esteps=(0, 6, 6000), T=300, wl=wl)
    print(a[3])
    plt.plot(a[0], a[1], label="N")
    plt.plot(a[0], a[2], label="K")

    fig, ax = plt.subplots(1,1)
    ax.plot(a[0], a[3])

    plt.legend()
    plt.show()
    print(a[3])
def task3():
    InSb = sopra_database('InAsSb')
task3()