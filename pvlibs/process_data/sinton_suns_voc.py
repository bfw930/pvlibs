
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

# savitzky-golay filter
from scipy.signal import savgol_filter


# wafer property calculation functions
from .wafer import calc_wafer_doping_density, calc_wafer_intrinsic, calc_wafer_equilibrium

# charge density dependent calculation functions
from .charge_density import calc_wafer_nonequilibrium



''' Core Calculation Functions '''

def calc_charge_density(_N_M, _n_i_eff, _wafer_thickness, _photovoltage):

    ''' Calculate Charge Density

        Calculate charge density as a function of time from measured photoconductance; ref: Dannhauser + Krausse Model

    Args:
        _N_M (float): doping density of majority carrier [ / cm^3]
        _wafer_thickness (float): wafer thickness [cm]
        _conductance (np.array): measured conductance [C]

    Returns:
        nd (np.array): excess minority carrier density [ / cm^3]
    '''



    ## Doping, Voc, ni

    nd = (((_N_M**2 + 4 * (_n_i_eff**2) * np.exp((const_q / (const_k * 298.15)) * _photovoltage))**0.5) - _N_M) / 2



    # return calculation results
    return nd



''' Data Processing Functions '''

def process_standard(_wafer_doping_type, _wafer_resistivity, _wafer_thickness, _wafer_optical_const,
                     _illumination_mode, _temperature,
                     _time, _conductance, _illumination):

    ''' Standard Sinton Lifetime Measurement Data Processsing

        Process imported sinton lifetime data, incorporate required experimental / device parameters; yield charge
        density and lifetime, doping density and implied suns

    Args:
        _wafer_doping_type
        _wafer_resistivity
        _wafer_thickness
        _wafer_optical_const
        _illumination_mode
        _temperature
        _time
        _conductance
        _illumination

    Returns:
        dict: calculated derivative data
    '''

    # calculate wafer donor, acceptor doping density
    N_D, N_A = calc_wafer_doping_density(_wafer_doping_type, _wafer_resistivity)

    # calculate majority carrier doping density
    N_M = np.max([N_D, N_A])


    # calculate excess minority carrier density
    nd = calc_charge_density(_N_M = N_M, _wafer_thickness = _wafer_thickness, _conductance = _conductance)




    # calculate effective intrinsic parameters
    N_c_i, N_v_i, E_c_i, E_v_i, n_i = calc_wafer_intrinsic(_T = _temperature)

    # calculate effective equilibrium parameters
    n_0, p_0, n_i_0 = calc_wafer_equilibrium(_T = _temperature, _N_D = N_D, _N_A = N_A, _E_c_i = E_c_i, _E_v_i = E_v_i,
                                             _N_c_i = N_c_i, _N_v_i = N_v_i, _n_i = n_i)



    # calculate implied suns
    isuns = ( nd * _wafer_thickness * 1.602e-19 / (0.038 * _wafer_optical_const * tau) )

    # get charge density at 1 sun
    j = np.where(isuns >= 1.)[0][-1]

    # calculate non-equilibrium parameters
    n, p, n_i_eff = calc_wafer_nonequilibrium(_T = _temperature, _N_D = N_D, _N_A = N_A, _E_c_i = E_c_i, _E_v_i = E_v_i,
                                              _N_c_i = N_c_i, _N_v_i = N_v_i, _n_i = n_i, _n_i_0 = n_i_0, _dn = nd[j],
                                              _dp = nd[j])


    # calculate implied Voc at 1 sun
    ivoc = ( (1.381e-23 * _temperature / 1.602e-19) * np.log(nd[j] * (N_M + nd[j]) / (n_i_eff**2)) )


    # return calculated results
    return N_D, N_A, nd, tau, isuns, n_i_eff, ivoc



def process_sinton_suns_voc(_db, _index, _process):

    ''' Process Sinton Lifetime Measurement Data

        Process imported sinton lifetime data, incorporate required experimental / device parameters; yield charge
        density and lifetime, doping density and implied suns

    Args:
        _db (dict): database instance
        _index (int): measurement node index within database instance measurement list
        _process (dict): measurement and process type details

    Returns:
        dict: calculated derivative data
    '''

    # process sinton lifetime measurement data
    if _process['process'] == 'standard':

        # get measurement node
        node = _db['measurement'][_index]

        illumination_mode = node['params']['illumination_mode']
        temperature = node['params']['temperature']
        time = node['data']['time']
        conductance = node['data']['conductance']
        illumination = node['data']['illumination']


        # get device state node from measurement node relation
        device_state = _db['device_state'][node['rels']['device_state'][0]]

        wafer_resistivity = device_state['params']['wafer_resistivity']
        wafer_thickness = device_state['params']['wafer_thickness']
        wafer_optical_const = device_state['params']['wafer_optical_const']


        # get device node from measurement node relation
        device = _db['device'][node['rels']['device'][0]]

        wafer_doping_type = device['params']['wafer_doping_type']


        # perform standard sinton lifetime measurement data processsing
        N_D, N_A, nd, tau, isuns, n_i_eff, ivoc = process_standard(_wafer_doping_type = wafer_doping_type,
                                                                   _wafer_resistivity = wafer_resistivity,
                                                                   _wafer_thickness = wafer_thickness,
                                                                   _wafer_optical_const = wafer_optical_const,
                                                                   _illumination_mode = illumination_mode,
                                                                   _temperature = temperature, _time = time,
                                                                   _conductance = conductance,
                                                                   _illumination = illumination)

        data = {'N_D': N_D, 'N_A': N_A, 'nd': nd, 'tau': tau, 'isuns': isuns, 'n_i_eff': n_i_eff, 'ivoc': ivoc}


        # return calculated results
        return data
