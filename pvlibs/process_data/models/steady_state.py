
'''

'''



''' Imports '''

# data array processing
import numpy as np


# fermi statistics functions
from .fermi_stats import calc_F_half, calc_F_half_inv

# general calculation functions
#from .general import calc_V_T



''' Non-Equilibrium Calculation Functions '''

def calc_gamma_bgn(_dE_c, _dE_v, _E_c_i, _E_v_i, _E_f_n, _E_f_p, _T):

    ''' Calculate Non-Equilibrium Bandgap Narrowing (BGN) Correction

        Calculates the BGN correction factor at non-equilibrium conditions

    Args:
        _dE_c (float): shift in conduction band energy due to bandgap narrowing [eV]
        _dE_v (float): shift in valance band energy due to bandgap narrowing [eV]
        _E_c_i (float): intrinsic conduction band energy relative to intrinsic Fermi level [eV]
        _E_v_i (float): intrinsic valance band energy relative to intrinsic Fermi level [eV]
        _E_f_n (float): electron Fermi level energy [eV]
        _E_f_p (float): hole Fermi level energy [eV]
        _T (float): temperature [K]
        _dE_c (float): shift in conduction band energy due to bandgap narrowing [eV]
        _dE_v (float): shift in valance band energy due to bandgap narrowing [eV]

    Returns:
        gamma_BGN_neq (float): bandgap narrowing correction factor [ ]
    '''

    # Boltzmann constant [J / K]
    k_B = 1.38065e-23

    # fundamental charge [C]
    q = 1.602176e-19


    # calculate electron Fermi statistics both with/without band energy shifts due to BGN
    F_n_bgn = calc_F_half(-((_E_c_i - _dE_c) - _E_f_n) / (k_B * _T / q))
    F_n = calc_F_half(-(_E_c_i - _E_f_n) / (k_B * _T / q))

    # calculate hole Fermi statistics both with/without band energy shifts due to BGN
    F_p_bgn = calc_F_half(-(_E_f_p - (_E_v_i + _dE_v)) / (k_B * _T / q))
    F_p = calc_F_half(-(_E_f_p - _E_v_i) / (k_B * _T / q))


    # calculate electron, hole bandgap narrowing correction factor
    gamma_n = F_n_bgn / F_n
    gamma_p = F_p_bgn / F_p

    # calculate bandgap narrowing correction factor [ ]
    gamma_bgn = gamma_n * gamma_p


    # return calculated BGN correction factor
    return gamma_bgn



def calc_gamma_noneq(_E_f_n, _E_f_p, _T):

    ''' Calculate Non-Equilibrium Correction Factor

        Calculates the non-equilibrium correction factor for n_i_eff calculation

    Args:
        _E_f_n (float): electron Fermi level energy [eV]
        _E_f_p (float): hole Fermi level energy [eV]
        _T (float): temperature [K]

    Returns:
        gamma_neq (float): non-equilibrium correction factor [ ]
    '''

    # Boltzmann constant [J / K]
    k_B = 1.38065e-23

    # fundamental charge [C]
    q = 1.602176e-19


    # calculate non-equilibrium correction factor [ ]
    gamma_noneq = np.exp(-(_E_f_p - _E_f_n) / (k_B * _T / q))


    # return calculated non-equilibrium correction factor
    return gamma_noneq
