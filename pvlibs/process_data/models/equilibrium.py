
'''

'''



''' Imports '''

# data array processing
import numpy as np


# fermi statistics functions
from .fermi_stats import calc_F_half, calc_F_half_inv

# general calculation functions
#from .general import calc_V_T



''' Equilibrium Silicon Calculation Functions '''

def calc_E_f_0(_E_c_0, _E_v_0, _n_0, _p_0, _T, _N_c_i, _N_v_i):

    ''' Calculate Equilibrium Fermi Level Energy

        Equilibrium Fermi energy level using Fermi-Dirac Statistics relative to ?? intrinsic Fermi level energy ??

    Args:
        _E_c_0 (float): equilibrium conduction band energy relative to intrinsic Fermi level [eV]
        _E_v_0 (float): equilibrium valance band energy relative to intrinsic Fermi level [eV]
        _n_0 (float): equilibrium electron concentration [ / cm^-3]
        _p_0 (float): equilibrium hole concentration [ / cm^-3]
        _T (float): temperature [K]
        _N_c_i (float): effective intrinsic conduction band density of states [ / cm^3]
        _N_v_i (float): effective intrinsic valance band density of states [ / cm^3]

    Returns:
        E_f_0 (float): equilibrium Fermi level energy [eV]
    '''

    # Boltzmann constant [J / K]
    k_B = 1.38065e-23

    # fundamental charge [C]
    q = 1.602176e-19


    # use fractional population of carrier DOS to calculate electron, hole Fermi statistics inverse of order 1/2 []
    F_inv_n = calc_F_half_inv(_f = (_n_0 / _N_c_i))
    F_inv_p = calc_F_half_inv(_f = (_p_0 / _N_v_i))


    # calculate equilibrium electron fermi energy level based on Fermi-Dirac statistics [eV]
    E_f_0 = (((F_inv_n - F_inv_p) * (k_B * _T / q)) + (_E_c_0 + _E_v_0)) / 2


    # return calculated equilibrium fermi energy
    return E_f_0



def calc_gamma_bgn_0(_N_c_i, _N_v_i, _n_0, _p_0, _T, _dE_c_0, _dE_v_0):

    ''' Calculate Equilibrium Bandgap Narrowing (BGN) Correction

        Calculates the BGN correction factor for intrinsic carrier concentration adjustment at equilibrium conditions

    Args:
        _N_c_i (float): effective intrinsic conduction band density of states [ / cm^3]
        _N_v_i (float): effective intrinsic valance band density of states [ / cm^3]
        _n_0 (float): electron concentration [ / cm^-3]
        _p_0 (float): hole concentration [ / cm^-3]
        _T (float): temperature [K]
        _dE_c_0 (float): shift in conduction band energy due to bandgap narrowing [eV]
        _dE_v_0 (float): shift in valance band energy due to bandgap narrowing [eV]

    Returns:
        gamma_BGN_0 (float): bandgap narrowing correction factor [ ]
    '''

    # Boltzmann constant [J / K]
    k_B = 1.38065e-23

    # fundamental charge [C]
    q = 1.602176e-19


    # use fractional DOS population to calculate electron, hole Fermi statistics with band energy shifts due to BGN
    F_n = calc_F_half( (_dE_c_0 / (k_B * _T / q)) + calc_F_half_inv(_f = (_n_0 / _N_c_i)) )
    F_p = calc_F_half( (_dE_v_0 / (k_B * _T / q)) + calc_F_half_inv(_f = (_p_0 / _N_v_i)) )

    # calculate bandgap narrowing correction factor [ ]
    gamma_bgn_0 = (F_n * F_p) / ((_n_0 / _N_c_i) * (_p_0 / _N_v_i))


    # return calculated BGN correction factor
    return gamma_bgn_0

