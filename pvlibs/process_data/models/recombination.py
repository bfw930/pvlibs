
'''

'''



''' Imports '''

# data array processing
import numpy as np



''' Recombination Lifetime Calculation Functions '''

def calc_tau_aug(_dn, _n, _p, _n_0, _p_0, _n_i_eff, _T):

    ''' Calculate Auger Recombination Lifetime

        Empirical model for auger recombination - Richter, 2012 []
            valid 300 K only

    Args:
        _dn (float): excess minority carrier concentration [ / cm^-3]
        _n (float): equilibrium electron concentration [ / cm^-3]
        _p (float): equilibrium hole concentration [ / cm^-3]
        _n (float): total electron concentration [ / cm^-3]
        _p (float): total hole concentration [ / cm^-3]
        _n_i_eff (float): effective intrinsic carrier concentration [ / cm^3]
        _T (float) - temperature [K]

    Returns:
        tau_aug (float): auger recombination lifetime [ / s]
    '''

    g_maxn = 235548 * _T**(-1.5013)
    g_maxp = 564812 * _T**(-1.6546)

    g_eeh = 1 + (g_maxn - 1) * (1 - np.tanh((_n_0 / 3.3e17)**(0.66)))
    g_ehh = 1 + (g_maxp - 1) * (1 - np.tanh((_p_0 / 7.0e17)**(0.63)))

    C_p = 2.5e-31; C_n = 8.5e-32; C_a = 3.0e-29

    C_p_eff = C_p * g_ehh
    C_n_eff = C_n * g_eeh

    invtau_auger_n = (C_n_eff * _n_0) * ((_n * _p - _n_i_eff**2) / _dn)
    invtau_auger_p = (C_p_eff * _p_0) * ((_n * _p - _n_i_eff**2) / _dn)
    invtau_auger_ambi = (C_a * _dn**0.92) * ((_n * _p - _n_i_eff**2) / _dn)


    # calculate auger recombination lifetime
    tau_aug = (invtau_auger_n + invtau_auger_p + invtau_auger_ambi)**-1


    # return calculated auger recombination lifetime
    return tau_aug


'''
    'Wang and MacDonald 2012 - validated for high injection only (deltaN = 5e16) between -30C and 200C on N_A = 5e15 cm-3 and 421um thk wafers, p-type

        C_a = (1.1E-28 / (TempInK - 193) + 2.1E-33 * TempInK) * ((delta_n / 5E+16) ^ (-0.2))

        tau_auger_calc = 1 / (C_a * delta_n ^ 2)


    'Altermatt 1997 - validated for 70-400K, low injection only for wafers with N_A > 1e16 cm-3 p-type wafers --> Need to fix

        g_maxn = 235548 * TempInK ^ (-1.5013)
        g_maxp = 564812 * TempInK ^ (-1.6546)

        g_eeh = 1 + (g_maxn - 1) * (1 - Application.WorksheetFunction.Tanh((n / 5E+16) ^ (0.34)))
        g_ehh = 1 + (g_maxp - 1) * (1 - Application.WorksheetFunction.Tanh((p / 5E+16) ^ (0.29)))

        C_p = 7.91E-32 - 4.13E-35 * (TempInK) + 3.59E-37 * (TempInK ^ 2) 'cm^6/s Modified from Dziewior and Schmid
        C_n = 2.8E-31 'cm^6/s From Dziewior and Schmid

        C_p_eff = C_p * g_ehh
        C_n_eff = C_n * g_eeh

        invtau_auger_n = (C_n_eff * n ^ 2 * p) / delta_n
        invtau_auger_p = (C_p_eff * p ^ 2 * n) / delta_n

        tau_auger_calc = 1 / (invtau_auger_n + invtau_auger_p)


    'Richter 2012 - validated for 300K only for all injection levels

        n_0 = n - delta_n
        p_0 = p - delta_n
        n_i_eff = (n_0 * p_0) ^ 0.5

        g_maxn = 14 '235548 * TempInK ^ (-1.5013)
        g_maxp = 8.5 '564812 * TempInK ^ (-1.6546)

        g_eeh = 1 + (g_maxn - 1) * (1 - Application.WorksheetFunction.Tanh((n_0 / 3.3E+17) ^ (0.66)))
        g_ehh = 1 + (g_maxp - 1) * (1 - Application.WorksheetFunction.Tanh((p_0 / 7E+17) ^ (0.63)))

        C_p = 2.5E-31   'cm^6/s @ 300K
        C_n = 8.5E-32   'cm^6/s @ 300K
        C_a = 3E-29     'cm^6/s @ 300K

        C_p_eff = C_p * g_ehh
        C_n_eff = C_n * g_eeh

        invtau_auger_n = (C_n_eff * n_0) * ((n * p - n_i_eff ^ 2) / delta_n)
        invtau_auger_n = (C_n_eff * n_0) * (n_0 + p_0 + delta_n)
        invtau_auger_p = (C_p_eff * p_0) * ((n * p - n_i_eff ^ 2) / delta_n)
        invtau_auger_ambi = (C_a * delta_n ^ 0.92) * ((n * p - n_i_eff ^ 2) / delta_n)

        tau_auger_calc = 1 / (invtau_auger_n + invtau_auger_p + invtau_auger_ambi)

'''



def calc_tau_rad(_dn, _n, _p, _n_i_eff, _T):

    ''' Calculate Radiative Recombination Lifetime

        Empirical model for radiative recombination lifetime - Altermatt et al, 2005
            valid 100 to 390 K

    Args:
        _dn (float): excess minority carrier concentration [ / cm^-3]
        _n (float): total electron concentration [ / cm^-3]
        _p (float): total hole concentration [ / cm^-3]
        _n_i_eff (float): effective intrinsic carrier concentration [ / cm^3]
        _T (float) - temperature [K]

    Returns:
        tau_r (float): radiative recombination lifetime [ / s]
    '''

    # B_low from Trupke et al, 2003
    B_low = 4.73e-15

    b_max = 1; r_max = 0.2; s_max = 1.5e18; w_max = 4.0e18
    r_min = 0; s_min = 1e7; w_min = 1e9

    b_2 = 0.54; r_1 = 320; s_1 = 550; w_1 = 365; b_4 = 1.25
    r_2 = 2.5; s_2 = 3; w_2 = 3.54

    b_1 = s_max + (s_min - s_max) / (1 + (_T / s_1)**s_2)
    b_3 = w_max + (w_min - w_max) / (1 + (_T / w_1)**w_2)
    b_min = r_max + (r_min - r_max) / (1 + (_T / r_1)**r_2)


    B_rel = b_min + (b_max - b_min) / (1 + ((_n + _p) / b_1)**b_2 + ((_n + _p) / b_3)**b_4)
    b = B_rel * B_low


    # calculate radiative recombination lifetime
    tau_r = _dn / (b * ((_n * _p) - _n_i_eff**2))


    # return calculated radiative recombination lifetime
    return tau_r



def calc_tau_sdr(_dn, _J_0, _N_M, _n_i_eff, _W):

    ''' Calculate Surface Defect Recombination

        Calculate total recombination lifetime from surface defect velocity, assumed identical at both surfaces

    Args:
        _dn (float): excess minority carrier density [ / cm^3]
        _N_M (float): net doping density of majority carrier [ / cm^3]
        _n_i_eff (float): effective intrinsic carrier concentration [ / cm^3]
        _J_0 (float): emitter recombination velocity [fA]
        _W (float): sample width [cm]

    Returns:
        tau_sdr (float): effective SRH recombination lifetime [ / s]
    '''

    # elementary charge [C]
    q = 1.602e-19

    # calculate recombination lifetime
    tau_sdr = ( _J_0 * (_N_M + _dn) / (_W * q * _n_i_eff**2) )**-1


    # return calculated surface defect recombination lifetime
    return tau_sdr



def calc_tau_srh(_dn, _N_M, _t_m0, _t_M0):

    ''' Calculate Shockley-Read-Hall (SRH) Recombintion (simple model)

    Args:
        _dn (float): excess minority carrier density [ / cm^3]
        _N_M (float): net doping density of majority carrier [ / cm^3]
        _t_m0 (float): lifetime of minority charge carrier [ / s]
        _t_M0 (float): lifetime of majority charge carrier [ / s]

    Returns
        tau_srh (float): effective SRH recombination lifetime [ / s]
    '''

    # calculate recombination lifetime
    tau_srh = (_t_m0 + _t_M0 * _dn / (_dn + _N_M))


    # return calculated effective SRH recombination lifetime
    return tau_srh



def calc_tau_srh_WIP(_dn, _N_M, _t_m0, _t_M0):

    ''' Calculate Shockley-Read-Hall (SRH) Recombintion ### WIP ###

        SRH recombintion lifetime incorporating trap energy levels

    Args:
        _dn (float): excess minority carrier density [ / cm^3]
        _N_M (float): net doping density of majority carrier [ / cm^3]
        _t_m0 (float): lifetime of minority charge carrier [ / s]
        _t_M0 (float): lifetime of majority charge carrier [ / s]

    Returns
        tau_srh (float): effective SRH recombination lifetime [ / s]
    '''


    #def func_srh(_delta_n, _N_dop, _t_n0, _t_p0, _n_i_eff, _wafer_type, _T, _E_t):

    #n, p = np_calc(_N_dop, _n_i_eff, _delta_n, _wafer_type, _T)


    # calculate energy levels from trap
    dE_t_v = (1.21 / 2) - _E_t
    dE_t_c = _E_t - (1.21 / 2)

    #
    p1 = _n_i_eff * np.exp( -dE_t_v / .0257 )
    n1 = _n_i_eff * np.exp( dE_t_c / .0257 )


    # R_SRH = ( n * p - n_i**2 ) / ( tau_p * ( n * n1 ) + tau_N * ( p * n2 ) )
    # n1 = N_c * exp( (E_t - E_c) / k_B * T )
    # p1 = N_v * exp( (E_v - E_t) / k_B * T )
    # k_np = (tau_p/tau_n)*(v_th_h/v_th_e)


    # calculate recombination lifetime
    #tau_srh = (_t_m0 + _t_M0 * _dn / (_dn + _N_M))
    tau_srh = ( (n * p - _n_i_eff**2) / ( _delta_n * ( _t_n0 * (p + p1) + _t_p0 * (n + n1) ) ) )**-1



    # return calculated effective SRH recombination lifetime
    return tau_srh
