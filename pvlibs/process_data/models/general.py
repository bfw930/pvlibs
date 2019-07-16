
'''
    General Calculation Functions

'''



''' Imports '''

# data array processing
import numpy as np



''' General Calculation Functions '''

def calc_V_T(_T):

    ''' Calculate Thermal Voltage

    Args:
        _T (float): temperature [K]

    Returns:
        V_T (float): thermal voltage [eV]
    '''

    # Boltzmann constant [J / K]
    k_B = 1.38065e-23

    # fundamental charge [C]
    q = 1.602176e-19

    # calculate thermal voltage for given temperature [eV]
    V_T = (k_B * _T / q)


    # return calculated thermal voltage
    return V_T
