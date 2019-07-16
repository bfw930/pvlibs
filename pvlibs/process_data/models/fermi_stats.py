
'''

'''



''' Imports '''

# data array processing
import numpy as np



''' Fermi Statistics Calculation Functions '''

def calc_F_half(_eta):

    ''' Calculate Fermi Statistics of Order 1/2

        Approximate Fermi integral of order 1/2 - Unger, Phys. Stat. Sol., 1988 [10.1002/pssb.2221490254]

    Args:
        _eta (float): energy level [J]

    Returns:
        F_half (float): Fermi Statistics of Order 1/2 [ ]
    '''

    z = np.log(1 + np.exp(_eta))

    if _eta <= 3:
        F_half = z + 0.1535 * z**2

    else:
        F_half = (4 / (3 * np.pi**0.5)) * (_eta**2 + 1.7788)**(3/4)


    # return calculated Fermi statistics
    return F_half



def calc_F_half_inv(_f):

    ''' Calculate Inverse Fermi Statistics of Order 1/2

        Approximate inverse Fermi integral of order 1/2 - Unger, Phys. Stat. Sol., 1988 [10.1002/pssb.2221490254]

    Args:
        _f (float): energy level [ ]

    Returns:
        F_half (float): Inverse Fermi statistics of order 1/2 [J]
    '''


    if _f < 1e-2: ## required to avoid div by zero error
        F_half_inv = np.log(_f + 1e-16)

    elif _f <= 4.475:
        F_half_inv = np.log(-1 + np.exp((-1 + (1 + 0.614 * _f)**(1/2)) / 0.307))

    else:
        F_half_inv = (((3/4) * _f * np.pi**(1/2))**(4/3) - 1.7788)**(1/2)


    # return calculated inverse Fermi statistics
    return F_half_inv



def calc_E_f(_E_c, _E_v, _n, _p, _T, _N_c_i, _N_v_i):

    ''' Calculate Fermi Level Energy

        Fermi energy level using Fermi-Dirac Statistics relative to intrinsic Fermi level energy

    Args:
        _E_c (float): conduction band energy relative to intrinsic Fermi level [eV]
        _E_v (float): valance band energy relative to intrinsic Fermi level [eV]
        _n (float): electron concentration [ / cm^-3]
        _p (float): hole concentration [ / cm^-3]
        _T (float): temperature [K]
        _N_c_i (float): intrinsic conduction band density of states [ / cm^3]
        _N_v_i (float): intrinsic valance band density of states [ / cm^3]

    Returns:
        E_f_n (float): electron Fermi level energy [eV]
        E_f_p (float): hole Fermi level energy [eV]
    '''

    # Boltzmann constant [J / K]
    k_B = 1.38065e-23

    # fundamental charge [C]
    q = 1.602176e-19


    # use fractional population of carrier DOS to calculate electron, hole Fermi statistics inverse of order 1/2 []
    F_inv_n = calc_F_half_inv(_f = (_n / _N_c_i))
    F_inv_p = calc_F_half_inv(_f = (_p / _N_v_i))


    # calculate steady-state electron, hole fermi energy level based on Fermi-Dirac statistics [eV]
    E_f_n = _E_c + (F_inv_n * (k_B * _T / q))
    E_f_p = _E_v - (F_inv_p * (k_B * _T / q))


    # return calculated electron, hole fermi energy
    return E_f_n, E_f_p



def calc_gamma_degen(_E_c, _E_v, _E_f_n, _E_f_p, _T):

    ''' Calculate Degeneracy Correction

        Calculates the degeneracy correction factor

    Args:
        _E_c (float): conduction band energy relative to equilibrium Fermi level [eV]
        _E_v (float): valance band energy relative to equilibrium Fermi level [eV]
        _E_f_n (float): electron Fermi level energy [eV]
        _E_f_p (float): hole Fermi level energy [eV]
        _T (float): temperature [K]

    Returns:
        gamma_degen (float): degeneracy correction factor [ ]
    '''

    # Boltzmann constant [J / K]
    k_B = 1.38065e-23

    # fundamental charge [C]
    q = 1.602176e-19


    # calculate electron, hole Fermi statistics
    F_p = calc_F_half(-(_E_f_p - _E_v) / (k_B * _T / q))
    F_n = calc_F_half(-(_E_c - _E_f_n) / (k_B * _T / q))

    exp_p = np.exp(-(_E_f_p - _E_v) / (k_B * _T / q))
    exp_n = np.exp(-(_E_c - _E_f_n) / (k_B * _T / q))

    # calculate non-equilibrium degeneracy correction factor [ ]
    gamma_degen = ((F_p / exp_p) * (F_n / exp_n))


    # return calculated degeneracy correction factor
    return gamma_degen
