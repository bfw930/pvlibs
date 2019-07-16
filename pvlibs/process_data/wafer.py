
''' Functions

Summary:
    This file contains

Example:
    Usage of

Todo:
    *
'''



''' Imports '''

# data array handling
import numpy as np


# model calculation functions
from . import models



''' Core Calculation Functions '''

def calc_wafer_doping_density(_wafer_doping_type, _wafer_resistivity):

    ''' Calculate Wafer Doping Density

        Calculate wafer donor, acceptor doping density from wafer resistivity; ref: Sinton Instruments

    Args:
        _wafer_doping_type (str): wafer doping type ['n-type' | 'p-type']
        _wafer_resistivity (float): wafer resistivity []

    Returns:
        N_D (float): calculated wafer donor doping density [ / cm^3]
        N_A (float): calculated wafer acceptor doping density [ / cm^3]
    '''

    # select coefficients by wafer type
    if _wafer_doping_type == 'n-type':
        a = [-6.34661e-4, 8.20326e-4, 0.01243, 0.04571, 0.07246, 1.07969, 15.69691]
    elif _wafer_doping_type == 'p-type':
        a = [-6.543e-4, 7.54055e-4, 0.0093332, 0.03469, 0.06473, 1.08286, 16.17944]

    # calculate wafer doping density
    wafer_doping_density = 10**( a[0] * np.log10(_wafer_resistivity)**6 + a[1] * np.log10(_wafer_resistivity)**5 +
                                 a[2] * np.log10(_wafer_resistivity)**4 - a[3] * np.log10(_wafer_resistivity)**3 +
                                 a[4] * np.log10(_wafer_resistivity)**2 - a[5] * np.log10(_wafer_resistivity) + a[6] )


    # set donor, acceptor doping density by wafer type
    if _wafer_doping_type == 'n-type':
        N_D = wafer_doping_density
        N_A = 0.
    elif _wafer_doping_type == 'p-type':
        N_D = 0.
        N_A = wafer_doping_density


    # return calculated wafer doping density
    return N_D, N_A



def calc_wafer_intrinsic(_T):

    ''' Get Effective Intrinsic Parameters

        Calculate and return intrinsic silicon parameters dependent only on temperature; band density of states,
        intrinsic bandgap, intrinsic carrier concentration

    Args:
        _T (float): temperature [K]

    Returns:
        N_c_i (float): effective intrinsic conduction band density of states [ / cm^3]
        N_v_i (float): effective intrinsic valance band density of states [ / cm^3]
        E_c_i (float): effective intrinsic conduction band energy relative to intrinsic Fermi level [eV]
        E_v_i (float): effective intrinsic valance band energy relative to intrinsic Fermi level [eV]
        n_i (float): effective intrinsic carrier density [ / cm^3]
    '''

    # calculate effective conduction, valance band density of states [ / cm^3]
    N_c_i, N_v_i = models.calc_N_i(_T = _T)

    # calculate effective intrinsic bandgap [eV]
    E_g_i = models.calc_E_g_i(_T = _T)

    # calculate effective intrinsic carrier density [ / cm^3]
    n_i = models.calc_n_i(_N_c_i = N_c_i, _N_v_i = N_v_i, _E_g_i = E_g_i, _T = _T)

    # calculate effective intrinsic Fermi level and conduction, valance band energy [eV]
    E_f_i, E_c_i, E_v_i = models.calc_E_f_i(_N_c_i = N_c_i, _N_v_i = N_v_i, _E_g_i = E_g_i, _T = _T)


    # return calculated parameters
    return N_c_i, N_v_i, E_c_i, E_v_i, n_i



def calc_wafer_equilibrium(_T, _N_D, _N_A, _E_c_i, _E_v_i, _N_c_i, _N_v_i, _n_i):

    ''' Get Equilibrium Parameters

        Calculate equilibrium parameters dependent on doping density and excess carrier densities; effective
        electron, hole carrier concentrations; iterate for convergence of effective intrinsic carrier density

    Args:
        _T (float): temperature [K]
        _N_D (float): donor doping concentration [ / cm^-3]
        _N_A (float): acceptor doping concentration [ / cm^-3]
        _N_c_i (float): intrinsic conduction band density of states [ / cm^3]
        _N_v_i (float): intrinsic valance band density of states [ / cm^3]
        _E_c_i (float): intrinsic conduction band energy relative to intrinsic Fermi level [eV]
        _E_v_i (float): intrinsic valance band energy relative to intrinsic Fermi level [eV]
        _n_i (float): effective intrinsic carrier concentration [ / cm^-3]

    Returns:
        n_0 (float): equilibrium electron concentration [ / cm^-3]
        p_0 (float): equilibrium hole concentration [ / cm^-3]
        n_i_0 (float): effective intrinsic carrier concentration at equilibrium [ / cm^-3]
    '''

    # initial guess (intrinsic/equilibrium values), calculate electron/hole conc.
    n_i_0 = _n_i


    # default initial reference to ensure initial iteration
    n_i_ref = 2 * n_i_0

    # set iteration params
    _iter = 0
    max_iter = 20


    # iterate for convergence of n_i to within 0.01% variation
    while (_iter <= max_iter) and ( abs((n_i_0 - n_i_ref) / n_i_ref) > 1e-4 ):

        # incriment iterator
        _iter += 1

        # update reference value for intrinsic carrier concentration convergence
        n_i_ref = n_i_0


        # calculate equilibrium electron, hole concentration [ / cm^-3], zero excess charge density
        n_0, p_0 = models.calc_np(_N_D = _N_D, _N_A = _N_A, _dn = 0, _dp = 0, _n_i = n_i_0)


        # calculate shift in conduction, valance band energy due to bandgap narrowing [eV]
        dE_g_0, dE_c_0, dE_v_0 = models.calc_dE_bgn(_N_D = _N_D, _N_A = _N_A, _n = n_0, _p = p_0, _T = _T)


        # calculate equilibrium bandgap narrowing correction factor [ ]
        gamma_bgn_0 = models.calc_gamma_bgn_0(_N_c_i = _N_c_i, _N_v_i = _N_v_i, _n_0 = n_0, _p_0 = p_0, _T = _T,
            _dE_c_0 = dE_c_0, _dE_v_0 = dE_v_0)


        # adjust intrinsic conduction, valance band energy due to bandgap narrowing
        E_c_0 = _E_c_i - dE_c_0
        E_v_0 = _E_v_i + dE_v_0


        # calculate equilibrium fermi level energy [eV]
        E_f_0 = models.calc_E_f_0(_E_c_0 = E_c_0, _E_v_0 = E_v_0, _n_0 = n_0, _p_0 = p_0, _T = _T, _N_c_i = _N_c_i,
            _N_v_i = _N_v_i)


        # using equivalent electron/hole fermi level, calculate equilibrium degeneracy factor [ ]
        gamma_degen_0 = models.calc_gamma_degen(_E_c = E_c_0, _E_v = E_v_0, _E_f_n = E_f_0, _E_f_p = E_f_0, _T = _T)


        # update effective intrinsic carrier concentration
        n_i_0 = ((_n_i**2) * gamma_bgn_0 * gamma_degen_0)**(0.5)


    # calculate equilibrium electron, hole concentration [ / cm^-3], zero excess charge density
    n_0, p_0 = models.calc_np(_N_D = _N_D, _N_A = _N_A, _dn = 0, _dp = 0, _n_i = n_i_0)


    # return calculated parameters
    return n_0, p_0, n_i_0
