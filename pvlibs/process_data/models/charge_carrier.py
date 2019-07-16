
'''

'''



''' Imports '''

# data array processing
import numpy as np


# general calculation functions
#from .general import calc_V_T



''' Silicon Charge Carrier Calculation Functions '''

def calc_np(_N_D, _N_A, _dn, _dp, _n_i):

    ''' Calculate Total Charge Carrier Concentration

    Args:
        _N_D (float): donor doping concentration [ / cm^-3]
        _N_A (float): acceptor doping concentration [ / cm^-3]
        _dn (float): excess electron concentration [ / cm^-3]
        _dp (float): excess hole concentration [ / cm^-3]
        _n_i (float): effective intrinsic carrier concentration [ / cm^-3]

    Returns:
        n (float): total electron concentration [ / cm^-3]
        p (float): total hole concentration [ / cm^-3]
    '''

    # net doping density
    N_net = _N_D - _N_A

    # assume complete ionisation of net doping concentration
    # apply law of mass action (n_0 * p_0 = n_i**2) for minority carrier concentration

    # n-type system or conditions
    if N_net >= 0:

        # calculate initial carrier concentrations
        n = (N_net / 2) + ((N_net / 2)**2 + _n_i**2)**(1/2)
        p = _n_i**2 / n

    # p-type system or conditions
    elif N_net < 0:

        # calculate initial carrier concentrations
        p = (N_net / 2) + ((N_net / 2)**2 + _n_i**2)**(1/2)
        n = _n_i**2 / p

    # calculate total equilibrium electron, hole concentrations
    n += _dn
    p += _dp


    # return calculated electron, hole concentration [ / cm^-3]
    return n, p



def calc_dE_bgn(_N_D, _N_A, _n, _p, _T):

    ''' Calculate Bandgap Narrowing Energy

        Analytical model of bandgap narrowing - Schenk J. App. Phys., 1998 [10.1063/1.368545]; implimentation by
        McIntosh, Altermatt 2010

    Args:
        _N_D (float): donor doping concentration [ / cm^-3]
        _N_A (float): acceptor doping concentration [ / cm^-3]
        _n (float): electron concentration [ / cm^-3]
        _p (float): hole concentration [ / cm^-3]
        _T (float): temperature [K]

    Returns:
        dE_g (float): total shift in bandgap energy due to narrowing [eV]
        dE_c (float): shift in conduction band energy due to bandgap narrowing [eV]
        dE_v (float): shift in valance band energy due to bandgap narrowing [eV]
    '''

    # k_B - Boltzmann constant [J / K]
    k_B = 1.38065e-23

    # q - fundamental charge [C]
    q = 1.602176e-19

    # mu_star is Reduced effective mass
    # m_e, m_h are DOS effective masses of electrons and holes, m_0 rest mass
    m_e_over_m_0 = 0.321
    m_h_over_m_0 = 0.346
    mu_star_over_m_0 = 0.1665

    Ry_ex = 16.55 / 1000 # meV, Excitonic Rydberg
    a_ex = 0.0000003719 # cm, Excitonic Bohr radius
    epsilon_s = 11.7 # Static dielectric constant

    # DOS/Carrier statistics - Degeneracy factors
    g_e = 12
    g_h = 4

    # total doping density
    N_sigma = _N_D + _N_A

    # Doping, DOS and carrier statistics
    # Dimensionless electron, hole conc
    n_e = _n * a_ex**3
    n_h = _p * a_ex**3
    n_sum = n_e + n_h

    alpha_e = mu_star_over_m_0 / m_e_over_m_0 # alpha_e = 0.5187
    alpha_h = mu_star_over_m_0 / m_h_over_m_0 # alpha_h = 0.4813
    n_p = alpha_e * n_e + alpha_h * n_h

    # Temperature dependent characteristics
    T_curly = (k_B * _T / q) / Ry_ex


    # Pade approximation for ionic shift
    h_e = 3.91
    h_h = 4.2
    j_e = 2.8585
    j_h = 2.9307
    k_e = 0.012
    k_h = 0.19
    q_e = 3 / 4
    q_h = 1 / 4

    # Ionic shift
    n_ionic = N_sigma * a_ex**3
    U_ionic = (n_sum**2) / (T_curly**3)

    delta_e_ionic = (-n_ionic) * (1 + U_ionic) * (((T_curly * n_sum / (2 * np.pi))**(1 / 2)) * (
        1 + h_e * np.log(1 + (n_sum**(1 / 2)) / T_curly)) + (
        (j_e * U_ionic * n_p**(3 / 4)) * (1 + k_e * n_p**q_e)))**(-1)

    delta_h_ionic = (-n_ionic) * (1 + U_ionic) * (((T_curly * n_sum / (2 * np.pi))**(1 / 2)) * (
        1 + h_h * np.log(1 + (n_sum**(1 / 2)) / T_curly)) + (
        (j_h * U_ionic * n_p**(3 / 4)) * (1 + k_h * n_p**q_h)))**(-1)


    # Ionic quasi-particle shifts
    delta_E_c_ionic = (-Ry_ex) * delta_e_ionic
    delta_E_v_ionic = (-Ry_ex) * delta_h_ionic


    # Pade approximation for rigid shift
    b_e = 8
    b_h = 1
    c_e = 1.3346
    c_h = 1.2365
    d_e = 0.893
    d_h = 1.153
    p_e = 7 / 30
    p_h = 7 / 30

    # Rigid shift
    delta_e_xc = -((((4 * np.pi)**3 * (n_sum)**2) * ((48 * n_e / (np.pi * g_e))**(1 / 3) + (
        c_e * np.log(1 + d_e * n_p**p_e)))) + (8 * np.pi * alpha_e * n_e * T_curly**2 / g_e) + (
        (8 * np.pi * n_sum)**(1 / 2) * T_curly**(5 / 2))) * (((4 * np.pi)**3 * n_sum**2) + (
        T_curly**3) + (b_e * (n_sum)**(1 / 2) * T_curly**2) + (40 * n_sum**(3 / 2) * T_curly))**(-1)

    delta_h_xc = -((((4 * np.pi)**3 * (n_sum)**2) * ((48 * n_h / (np.pi * g_h))**(1 / 3) + (
        c_h * np.log(1 + d_h * n_p**p_h)))) + (8 * np.pi * alpha_h * n_h * T_curly**2 / g_h) + (
        (8 * np.pi * n_sum)**(1 / 2) * T_curly**(5 / 2))) * (((4 * np.pi)**3 * n_sum**2) + (
        T_curly**3) + (b_h * (n_sum)**(1 / 2) * T_curly**2) + (40 * n_sum**(3 / 2) * T_curly))**(-1)

    # Rigid quasi-particle shifts of conduction, valence bands
    delta_E_c_xc = (-Ry_ex) * delta_e_xc
    delta_E_v_xc = (-Ry_ex) * delta_h_xc


    # calculate total shift in conduction, valance band energy [eV]
    dE_c = delta_E_c_xc + delta_E_c_ionic
    dE_v = delta_E_v_xc + delta_E_v_ionic

    # calculate total bandgap narrowing [eV]
    dE_g = dE_c + dE_v


    # return calculated shift in conduction, valance band energy due to bandgap narrowing
    return dE_g, dE_c, dE_v


