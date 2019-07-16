
''' Core Orchestration Protocols

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

# simple linear regression
from scipy.stats import linregress


# database search functions
from .. import database



''' Core Calculation Functions '''

def calc_performance(_data, _params):

    ''' Calculate Doping Density

        Calculate device performance from 1 sun current-voltage measurement

    Args:
        _data (dict): 1 sun current-voltage measurement node data
        _params (dict): required device node parameters

    Returns:
        dict: calculated derivative data
    '''

    calc_params = {}

    # unpack required device parameters
    A = _params['wafer_area']
    calc_params['area'] = A

    # get IV data
    I = -_data['current'][::-1]
    calc_params['current'] = I

    V = _data['voltage'][::-1]
    calc_params['voltage'] = V


    # calculate short circuit current
    j = np.where(V < 0)[0][-1]
    Isc = np.mean(I[j:j+2])
    calc_params['isc'] = Isc


    # calculate open circuit voltage
    j = np.where(I > 0)[0][-1]
    Voc = np.mean(V[j:j+2])
    calc_params['voc'] = Voc


    # calculate power at max power point
    P = I * V
    Pmpp = P.max()
    calc_params['pmpp'] = Pmpp


    # calculate current / voltage at max power point
    j = np.where(P == Pmpp)[0][0]
    Impp = I[j]
    calc_params['impp'] = Impp
    Vmpp = V[j]
    calc_params['vmpp'] = Vmpp


    # calculate fill factor
    FF = Pmpp / (Isc * Voc)
    calc_params['ff'] = FF


    # calculate solar conversion efficiency
    Eta = (Isc * Voc * FF) / (100 * A)
    calc_params['eta'] = Eta


    # return calculation results
    return calc_params



def calc_shunt_resistance(_data, _params):

    ''' Calculate Shunt Resistance

        Calculate shunt resistance from reverse bias region of dark current-voltage response

    Args:
        _data (dict): dark current-voltage measurement node data
        _params (dict): required device node parameters

    Returns:
        dict: calculated derivative data
    '''

    calc_params = {}

    # get IV data
    I = -_data['current'][::-1]
    #calc_params['current'] = I

    V = _data['voltage'][::-1]
    #calc_params['voltage'] = V


    # filter for only low reverse bias region
    j = np.where( (V >= -3.) & (V <= 0.) )[0]
    I = I[j]
    V = V[j]

    # perform linear regression to calculate slope
    slope, intercept, err, a, b = linregress(V, I)

    # calculate shunt resistance from negative inverse slope
    calc_params['rp'] = -slope**-1


    # return calculation results
    return calc_params



def calc_series_resistance(_full_data, _half_data, _params):

    ''' Calculate Series Resistance

        Calculate series resistance from 1 sun and half sun current-voltage responses

    Args:
        _full_data (dict): 1 sun current-voltage measurement node data
        _half_data (dict): half sun current-voltage measurement node data
        _params (dict): required device node parameters

    Returns:
        dict: calculated derivative data
    '''

    # given two points ([x1, x2], [y1, y2]) and y value, return x at y
    def get_y(p1, p2, y):
        m = (p2[1] - p1[1]) / (p2[0] - p1[0])
        b = p2[1] - (m * p2[0])
        return (y - b) / m


    # given two points ([x1, x2], [y1, y2]) and x value, return y at x
    def get_x(p1, p2, x):
        m = (p2[1] - p1[1]) / (p2[0] - p1[0])
        b = p2[1] - (m * p2[0])
        return m * x + b


    calc_params = {}


    # get IV data
    I_f = -_full_data['current'][::-1]
    V_f = _full_data['voltage'][::-1]

    #calc_params['full_current'] = I_f
    #calc_params['full_voltage'] = V_f


    I_h = -_half_data['current'][::-1]
    V_h = _half_data['voltage'][::-1]

    #calc_params['half_current'] = I_h
    #calc_params['half_voltage'] = V_h


    # calculate short circuit current
    j = np.where(V_f < 0)[0][-1]
    Isc_f = get_x([V_f[j], I_f[j]], [V_f[j+1], I_f[j+1]], 0)

    j = np.where(V_h < 0)[0][-1]
    Isc_h = get_x([V_h[j], I_h[j]], [V_h[j+1], I_h[j+1]], 0)


    # set delta in I of 5% 1 sun Isc
    dIsc = Isc_f * 0.05
    Rs = []

    # calculate series resistance using 1 sun and 1/2 sun IV method, average of 6 points, ref (10.1002/pip.1216)
    for i in range(1,7):

        # set I value from increasing delta I relative to Isc
        I_f_ = Isc_f - dIsc * i
        I_h_ = Isc_h - dIsc * i

        # get V at each I using 2 point gradient
        j = np.where(I_f > I_f_)[0][-1]
        V_f_ = get_y([V_f[j], I_f[j]], [V_f[j+1], I_f[j+1]], I_f_)

        j = np.where(I_h > I_h_)[0][-1]
        V_h_ = get_y([V_h[j], I_h[j]], [V_h[j+1], I_h[j+1]], I_h_)


        # calculate series resistance from slope
        Rs.append( (V_h_ - V_f_) / (I_f_ - I_h_) )

    # calculate series resistance from average over points
    calc_params['rs'] = np.mean(Rs)


    # return calculation results
    return calc_params



''' Data Processing Functions '''

def process_standard(device_state_params, full_data, half_data, dark_data):

    ''' Process Current-Voltage Measurements

        Process imported current-voltage measurement data for a given measurment, incorporate required
        experimental / device parameters; yield performance parameters, derivative values

    Args:


    Returns:
        dict: calculated derivative data
    '''

    # calculate device solar performance from 1 sun current-voltage data
    performance_data = calc_performance(_data = full_data, _params = device_state_params)

    # calculate cell shunt resistance from dark current-voltage response
    shunt = calc_shunt_resistance(_data = dark_data, _params = device_state_params)

    # calculate cell series resistance from full and half 1 sun current-voltage response
    series = calc_series_resistance(_full_data = full_data, _half_data = half_data,
        _params = device_state_params)


    # aggregate data
    results = {**performance_data, **series, **shunt}

    # current density
    results['jsc'] = (results['isc']) / results['area']
    results['jmpp'] = (results['impp']) / results['area']


    # calculate series adjusted area values [Ohm cm^2]
    results['rs_sqr'] = results['rs'] * results['area'] * 1e3
    results['rp_sqr'] = results['rp'] * results['area'] * 1e3


    # Power Loss over Rs in mW/sqr (Ps = Rs x Jmpp^2)
    results['loss_rs'] = (results['rs_sqr'] * 1e-3) * results['jmpp']**2

    # Voltage over shunt resistor (Vp = Vmpp + Rs x Jmpp)
    Vp = (results['vmpp'] * 1e-3) + ((results['rs_sqr'] * 1e-3) * results['jmpp'])

    # Power loss over shunt resistor in mW/sqr (Pp = Vp^2 / Rp)
    results['loss_rp'] = (Vp**2) / (results['rp_sqr'] * 1e-3)

    # The power loss in the diode due to the forward bias voltage in mW/sqr (Pf = Vp x (Jsc - Jmpp)
    results['loss_mpp'] = Vp * (results['jsc'] - results['jmpp'])


    # return calculated results
    return results


def iv(data):

    ''' Process Current-Votlage Measurements

        Process imported current-voltage measurement data for a given measurment, incorporate required
        experimental / device parameters; yield performance parameters, derivative values

    Args:
        _db (dict): database instance

    Returns:
        dict: calculated derivative data
    '''

    full_data = data['full']
    half_data = data['half']
    dark_data = data['dark']


    # perform calculations, return results
    results = process_standard(device_state_params = data, full_data = full_data,
        half_data = half_data, dark_data = dark_data)


    # return calculated results
    return results
