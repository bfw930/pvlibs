
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

def calc_wafer_nonequilibrium(_T, _N_D, _N_A, _E_c_i, _E_v_i, _N_c_i, _N_v_i, _n_i, _n_i_0, _dn, _dp):

    ''' Get Steady State Parameters

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
        _n_i_0 (float): equilibrium effective intrinsic carrier concentration [ / cm^-3]
        _dn (float): excess electron concentration [ / cm^-3]
        _dp (float): excess hole concentration [ / cm^-3]

    Returns:
        n_0 (float): non-equilibrium total electron concentration [ / cm^-3]
        p_0 (float): non-equilibrium total hole concentration [ / cm^-3]
        n_i_eff (float): non-equilibrium effective intrinsic carrier concentration [ / cm^-3]
    '''

    # initial guess (intrinsic/equilibrium values), calculate electron/hole conc.
    n_i_eff = _n_i_0


    # default initial reference to ensure initial iteration
    n_i_ref = 2 * n_i_eff

    # set iteration params
    _iter = 0
    max_iter = 20


    # iterate for convergence of n_i to within 0.01% variation
    while (_iter <= max_iter) and ( abs((n_i_eff - n_i_ref) / n_i_ref) > 1e-4 ):

        # incriment iterator
        _iter += 1

        # update reference value for intrinsic carrier concentration convergence
        n_i_ref = n_i_eff


        # calculate equilibrium electron, hole concentration [ / cm^-3], zero excess charge density
        n, p = models.calc_np(_N_D = _N_D, _N_A = _N_A, _dn = _dn, _dp = _dp, _n_i = n_i_eff)


        # calculate shift in conduction, valance band energy due to bandgap narrowing [eV]
        dE_g, dE_c, dE_v = models.calc_dE_bgn(_N_D = _N_D, _N_A = _N_A, _n = n, _p = p, _T = _T)


        # adjust intrinsic conduction, valance band energy due to bandgap narrowing
        E_c = _E_c_i - dE_c
        E_v = _E_v_i + dE_v


        # calculate electron, hole fermi energy level [eV]
        E_f_n, E_f_p = models.calc_E_f(_E_c = E_c, _E_v = E_v, _n = n, _p = p, _T = _T, _N_c_i = _N_c_i,
                                       _N_v_i = _N_v_i)


        # calculate bandgap narrowing correction factor [ ]
        gamma_bgn = models.calc_gamma_bgn(_dE_c = dE_c, _dE_v = dE_v, _E_c_i = _E_c_i, _E_v_i = _E_v_i,
            _E_f_n = E_f_n, _E_f_p = E_f_p, _T = _T)


        # calculate degeneracy factor [ ]
        gamma_degen = models.calc_gamma_degen(_E_c = E_c, _E_v = E_v, _E_f_n = E_f_n, _E_f_p = E_f_p, _T = _T)


        # calculate non-equilibrium correction factor [ ]
        gamma_noneq = models.calc_gamma_noneq(_E_f_n = E_f_n, _E_f_p = E_f_p, _T = _T)


        # update effective intrinsic carrier concentration
        n_i_eff = ((_n_i**2) * gamma_bgn * gamma_degen)**0.5


    # calculate non-equilibrium electron, hole concentration [ / cm^-3]
    n, p = models.calc_np(_N_D = _N_D, _N_A = _N_A, _dn = _dn, _dp = _dp, _n_i = n_i_eff)


    # return calculated parameters
    return n, p, n_i_eff
