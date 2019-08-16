
'''

'''



''' Imports '''

# data array processing
import numpy as np



''' Intrinsic Silicon Calculation Functions '''



def calc_v_th(_T):

    ''' Calculate Charge Carrier Thermal Velocity

    Calculates thermal velocity of electrons in cm/s [model: Green 1990]

    Args:
        _T (float): temperature [K]

    Returns:
        v_th_e (float): intrinsic thermal velocity of electrons [cm / s]
        v_th_h (float): intrinsic thermal velocity of holes [cm / s]
    '''

    # Boltzmann constant [J / K]
    k_B = 1.38065e-23

    # m_0 is rest mass of electron [kg]
    m_0 = 9.10938e-31

    ## calculate electron thermal velocity

    # model params
    m_t_star = 0.1905 # transverse effective mass
    m_l_star = 0.9163 # longitudinal effective mass

    # a, b, c, Bandgap calc terms
    a = 1.1785
    b = -9.025e-5
    c = -3.05e-7

    # Electrons (conduction band)
    E_g_T = a + b * _T + c * (_T**2)
    m_t_star = m_t_star * a / E_g_T
    delta = ((m_l_star - m_t_star) / m_l_star)**0.5

    # Electron Thermal mass for conduction band
    m_tc_star = 4 * m_l_star / ((1 + (m_l_star / m_t_star)**0.5 * np.arcsin(delta) / delta)**2)

    # calculate thermal velocity electrons
    v_th_e = ( (8 * k_B * _T / (np.pi * m_tc_star * m_0))**0.5 ) * 100


    ## calculate hole thermal velocity

    # Params for valence band thermal mass empirical model [Lang 1981]
    a = 0.443587; b = 3.609528e-3; c = 1.173515e-4; d = 1.263218e-6; e = 3.025581e-9
    f = 4.683382e-3; g = 2.286895e-4; h = 7.469271e-7; i = 1.727481e-9

    # Hole thermal mass for valence band
    m_dv_star = ((a + b * _T + c * _T**2 + d * _T**3 + e * _T**4) / (1 + f * _T + g * _T**2 + h * _T**3 +
                                                                     i * _T**4))**(2 / 3)

    # Thermal velocity
    v_th_h = ( (8 * k_B * _T / (np.pi * m_dv_star * m_0))**0.5 ) * 100


    # return calculated intrinsic thermal velocity of electrons, holes
    return v_th_e, v_th_h



def calc_E_g_i(_T, _E_g_0 = 1.17):

    ''' Calculate Effective Intrinsic Bandgap

    Empirical model for temperature dependence of intrinsic bandgap; Paessler, Phys. Rev. B, 2002
    [10.1103/PhysRevB.66.085201]
        validated up to 415K

    Args:
        _T (float): temperature [K]
        _E_g_0 (float): intrinsic bandgap of Silicon at 0 K [eV], default 1.17

    Returns:
        E_g_i (float): effective intrinsic bandgap [eV]
    '''

    alpha = 3.23e-4 # [eV / K]
    theta = 4.46e+2 # [K]
    delta = 5.10e-1 # []

    gamma = (1 - 3 * delta**2) / (np.exp(theta / _T) - 1) # []
    chi = 2 * _T / theta # []

    # E_g_T - temperature dependence adjustment to intrinsic bandgap [eV]
    E_g_T = alpha * theta * ( gamma + ((3/2) * delta**2) * (( 1 + (np.pi**2 / (3 * (1 + delta**2))) * chi**2 +
                             ((3 * delta**2 - 1) / 4) * chi**3 + (8/3) * chi**4 + chi**6 )**(1/6) - 1) )

    # E_g_i - effective intrinsic bandgap [eV]
    E_g_i = _E_g_0 - E_g_T


    # return calculated effective intrinsic bandgap
    return E_g_i



def calc_N_i(_T):

    ''' Calculate Effective Intrinsic Band Density of States

    Empirical model for mass constant; Couderc, J. App. Phys., 2014 [10.1063/1.4867776]
        validated up to 500K

    Args:
        _T (float): temperature [K]

    Returns:
        N_c (float): effective conduction band density of states [ / cm^3]
        N_v (float): effective valance band density of states [ / cm^3]
    '''

    A_c = [-4.609e-10,  6.753e-7 , -1.312e-5 ,  1.094e+0 ]
    A_v = [ 2.525e-9 , -4.689e-6 ,  3.376e-3 ,  3.426e-1 ]

    N_i = []
    # iterate conduction, valance band
    for A in [A_c, A_v]:

        # m - empirical effective mass constant []
        m = A[0] * _T**3 + A[1] * _T**2 + A[2] * _T + A[3]

        # N - effective density of states in the conduction / valance band [ / cm^3]
        N_i.append( 4.83e15 * m * _T**(3/2) )

    # unpack conduction, valance band values
    N_c_i, N_v_i = N_i


    # return calculated effective conduction, valance band density of states
    return N_c_i, N_v_i



def calc_E_f_i(_N_c_i, _N_v_i, _E_g_i, _T):

    ''' Calculate Intrinsic Fermi Level Energy

        Calculate the intrinsic Fermi level energy and that of conduction, valance bands

    Args
        _N_c_i (float): effective intrinsic conduction band density of states [ / cm^3]
        _N_v_i (float): effective intrinsic valance band density of states [ / cm^3]
        _E_g_i (float): effective intrinsic bandgap [eV]
        _T (float): temperature [K]

    Returns:
        E_f_i (float): intrinsic Fermi level [eV]
        E_c_i (float): intrinsic conduction band energy relative to intrinsic Fermi level [eV]
        E_v_i (float): intrinsic valance band energy relative to intrinsic Fermi level [eV]
    '''

    # Boltzmann constant [J / K]
    k_B = 1.38065e-23

    # fundamental charge [C]
    q = 1.602176e-19


    # calculate effective intrinsic Fermi level [eV]
    E_f_i = (_E_g_i / 2) + ( (k_B * _T / q) / 2) * np.log(_N_c_i / _N_v_i)


    # calculate conduction, valance band edge relative to the intrinsic fermi level [eV]
    E_c_i = _E_g_i - E_f_i
    E_v_i = - E_f_i


    # return calculated effective intrinsic Fermi level
    return E_f_i, E_c_i, E_v_i



def calc_n_i(_N_c_i, _N_v_i, _E_g_i, _T):

    ''' Calculate Effective Intrinsic Carrier Density

        Couderc, J. App. Phys., 2014 [10.1063/1.4867776]
            valid for 77-375K

    Args
        _N_c_i (float): effective intrinsic conduction band density of states [ / cm^3]
        _N_v_i (float): effective intrinsic valance band density of states [ / cm^3]
        _E_g_i (float): effective intrinsic bandgap [eV]
        _T (float): temperature [K]

    Returns:
        n_i (float): intrinsic carrier density [ / cm^3]
    '''

    # k_B - boltzmann constant [eV / K]
    k_B = 8.61733e-5

    # n_i - intrinsic carrier density [ / cm^3]
    n_i = ( _N_c_i * _N_v_i * np.exp( -_E_g_i / (k_B * _T) ) )**(1/2)


    # return calculated intrinsic carrier density
    return n_i
