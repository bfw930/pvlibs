
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


from scipy.stats import linregress

from scipy.interpolate import splev, splrep




''' Core Calculation Functions '''

def calc_charge_density(_N_M, _wafer_thickness, _conductance):

    ''' Calculate Charge Density

        Calculate charge density as a function of time from measured photoconductance; ref: Dannhauser + Krausse Model

    Args:
        _N_M (float): doping density of majority carrier [ / cm^3]
        _wafer_thickness (float): wafer thickness [cm]
        _conductance (np.array): measured conductance [C]

    Returns:
        nd (np.array): excess minority carrier density [ / cm^3]
    '''

    # calculate initial estimate of charge density
    n_0 = _conductance / (_wafer_thickness * 1700 * 1.6e-19)

    # refine charge density calculation
    n_1 = ( n_0 * 1700 / ( 1800 * (1 + 10**( 0.8431 * np.log10( (n_0 + _N_M) / 1.2e18 ) )) /
                                  (1 + 8.36 * 10**(0.8431 * np.log10( (n_0 + _N_M) / 1.2e18 )))) )

    # calculate apparent excess minority carrier density
    nd = ( n_1 * (1800 * (1 + 10**(0.8431 * np.log10((n_0 + _N_M) / 1.2E+18))) /
                         (1 + 8.36 * 10**(0.8431 * np.log10((n_0 + _N_M) / 1.2e18)))) /
                 (1800 * (1 + 10**(0.8431 * np.log10((n_1 + _N_M) / 1.2e18))) /
                         (1 + 8.36 * 10**(0.8431 * np.log10((n_1 + _N_M) / 1.2e18)))) )


    # return calculation results
    return nd



def calc_lifetime(_time, _nd, _illumination, _wafer_optical_const, _wafer_thickness, _illumination_mode):

    ''' Calculate Lifetime

        Calculate minority charge carrier lifetime as a function of time from charge density derivative; ref: Sinton
        Instruments

    Args:
        _time (np.array): measurement time [s]
        _nd (np.array): minority carrier density [ / cm^3]
        _illumination (np.array): illumination photon density [ / cm^3]
        _wafer_optical_const (float): wafer optical constant [ ]
        _wafer_thickness (float): wafer thickness [cm]
        _illumination_mode: measurement illumination mode ['gen' | 'trans']

    Returns:
        lifetime (np.array): calculated minority charge carrier lifetime
    '''

    ## calculate derevative of charge density with respect to time

    # get sampling rate (s)
    sample_rate = _time.ptp() / (_time.shape[0] - 1)

    # apply savitzky-golay filter with minimal smoothing, obtain derivative, adjust for sameple rate
    nd_deriv = savgol_filter(_nd, window_length = 21, polyorder = 3, deriv = 1) / sample_rate


    ## calculate minority carrier lifetime by measurement illumination mode

    # for generalised illumination mode
    if _illumination_mode == 'gen':

        lifetime = (_nd * _wafer_thickness) / (_illumination * _wafer_optical_const - (_wafer_thickness * nd_deriv))

    # for transient illumination mode
    elif _illumination_mode == 'trans':

        lifetime = -_nd / nd_deriv


    # return calculation results
    return lifetime



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


    # calculate minority carrier lifetime
    tau = calc_lifetime(_time = _time, _nd = nd, _illumination = _illumination,
                        _wafer_optical_const = _wafer_optical_const, _wafer_thickness = _wafer_thickness,
                        _illumination_mode = _illumination_mode)


    # calculate effective intrinsic parameters
    N_c_i, N_v_i, E_c_i, E_v_i, n_i = calc_wafer_intrinsic(_T = _temperature)

    # calculate effective equilibrium parameters
    n_0, p_0, n_i_0 = calc_wafer_equilibrium(_T = _temperature, _N_D = N_D, _N_A = N_A, _E_c_i = E_c_i, _E_v_i = E_v_i,
                                             _N_c_i = N_c_i, _N_v_i = N_v_i, _n_i = n_i)


    # calculate implied suns
    isuns = ( nd * _wafer_thickness * 1.602e-19 / (0.038 * _wafer_optical_const * tau) )


    # calculate non-equilibrium parameters over charge density range
    n_i_eff = np.array([
        calc_wafer_nonequilibrium(_T = _temperature, _N_D = N_D, _N_A = N_A, _E_c_i = E_c_i,
            _E_v_i = E_v_i, _N_c_i = N_c_i, _N_v_i = N_v_i, _n_i = n_i, _n_i_0 = n_i_0, _dn = dn, _dp = dn)
        for dn in nd ])[:,2]

    # calculate implied Voc
    ivocs = ( (1.381e-23 * _temperature / 1.602e-19) * np.log(nd * (N_M + nd) / (n_i_eff**2)) )


    # get charge density at 1 sun
    j = np.where(isuns[::-1] >= 1.)[0]

    # handle case for isuns max less than 1 sun
    if len(j) > 0:
        k = len(isuns) - j[0] - 1
        ivoc = ivocs[k]

    else:
        # linear regression for ivoc at 1 sun
        x = np.log(isuns)
        y = ivocs
        j = np.where((x > -5))
        m, b, std, err1, err2 = linregress(x = x[j], y = y[j])
        ivoc = b


    ''' pseudo-FF calc '''

    if True:

        # sort data
        j = np.argsort(ivocs)
        _ivocs = ivocs[j]
        _isuns = isuns[j]

        # get 1 sun voc
        spl = splrep(_isuns, _ivocs)
        voc = splev(1., spl, der = 0)

        # extrapolate suns-voc from log-linear regression
        slope, icept, err1, err1, err3 = linregress(_ivocs, np.log(_isuns))
        V = np.arange(.1, .8, .01)
        iss = np.exp(slope*V + icept)

        I = -(iss-1)
        P = I*V

        j = np.where(I >= 0.)
        I = I[j]
        V = V[j]
        P = P[j]


        # rough maximum power point
        k = np.where(P == P.max())
        Vj = V[j][k]

        # b-pline fit around maximum power point (rel. power)
        k = np.where( (V[j] > Vj-0.1) & (V[j] < Vj+0.1) )
        spl = splrep( V[j][k], P[k], )

        # derivative of power at maximum power point
        xr = np.arange(Vj-0.05, Vj+0.025, .001)
        dP = splev(xr, spl, der = 1)

        # linear regression for maximum power point voltage
        slope, icept, r_value, p_value, std_err = linregress(dP, xr)
        Vmpp = icept

        # power at maximum power point
        Pmpp = splev(Vmpp, spl, der = 0)

        # b-pline fit around maximum power point (rel. power)
        spl = splrep(V, I)
        Impp = splev(Vmpp, spl, der = 0)

        pFF = Impp*Vmpp/(1.*voc)

    # temp
    pFF = .99


    # return calculated results
    return N_D, N_A, nd, tau, isuns, n_i_eff, ivoc, ivocs, pFF



def quick_process(params, data):

    ''' Quick Process

    Args:
        _db (dict): database instance

    Returns:
        dict: calculated derivative data
    '''

    illumination_mode = params['illumination_mode']
    temperature = params['temperature']

    time = data['time']
    conductance = data['conductance']
    illumination = data['illumination']

    wafer_thickness = params['wafer_thickness']
    wafer_optical_const = params['wafer_optical_const']
    wafer_doping_type = params['wafer_doping_type']


    wafer_resistivity = params['wafer_resistivity']

    # use calculated wafer resistivity
    #wafer_resistivity = data['dark_res'] * wafer_thickness


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

    calc_wafer_resistivity = data['dark_res'] * wafer_thickness

    data['calc_wafer_resistivity'] = calc_wafer_resistivity


    # return calculated results
    return data




def slt(data):

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

    illumination_mode = data['illumination_mode']
    temperature = data['temperature']
    time = data['time']
    conductance = data['conductance']
    illumination = data['illumination']
    wafer_resistivity = data['wafer_resistivity']
    wafer_thickness = data['wafer_thickness']
    wafer_optical_const = data['wafer_optical_const']
    wafer_doping_type = data['wafer_doping_type']


    if 'trim-slt' in data.keys():
        trim = data['trim-slt']
    else:
        trim = True

    # use voltage transient derivatives to trim start and end, remove error values and noise
    if trim:

        # select data range
        x = time.copy()
        y = conductance.copy()
        z = illumination.copy()

        # strip error values at head and tail (time and noise floor)
        j = np.where( (x > 0.) & (y > 2e-4) )
        x = x[j]; y = y[j]; z = z[j]

        # calculate first derivative
        dy = savgol_filter(y, 15, 2, deriv = 1, mode = 'nearest')
        ddy = savgol_filter(y, 15, 2, deriv = 2, mode = 'nearest')

        # strip error values
        j = np.where( (y > 1e-3) & (dy > 0.) )[0]
        if len(j) > 0:
            x = x[(j[-1]+1):]
            y = y[(j[-1]+1):]
            z = z[(j[-1]+1):]
            dy = dy[(j[-1]+1):]
            ddy = ddy[(j[-1]+1):]

        k = np.where( (ddy == ddy.max()) )[0][0]
        j = np.where( (ddy < 0.) & (x < x[k]) )[0]
        if len(j) > 0:
            x = x[(j[-1]+1):]
            y = y[(j[-1]+1):]
            z = z[(j[-1]+1):]

        # update raw data
        time = x
        conductance = y
        illumination = z



    # perform standard sinton lifetime measurement data processsing
    N_D, N_A, nd, tau, isuns, n_i_eff, ivoc, ivocs, pFF = process_standard(_wafer_doping_type = wafer_doping_type,
                                                               _wafer_resistivity = wafer_resistivity,
                                                               _wafer_thickness = wafer_thickness,
                                                               _wafer_optical_const = wafer_optical_const,
                                                               _illumination_mode = illumination_mode,
                                                               _temperature = temperature, _time = time,
                                                               _conductance = conductance,
                                                               _illumination = illumination)

    results = {'N_D': N_D, 'N_A': N_A, 'nd': nd, 'tau': tau, 'isuns': isuns, 'n_i_eff': n_i_eff, 'ivoc': ivoc,
        'ivocs': ivocs, 'pFF': pFF}


    results['calc_wafer_resistivity'] = data['dark_res'] * wafer_thickness


    # return calculated results
    return results
