
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

# b-spline interpolation
from scipy.interpolate import splev, splrep


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


    # get current, voltage under 1 sun illumination
    l = 'full'
    V = _data['voltage']
    I = _data['current']

    # sort data on voltage (start low)
    j = np.argsort(V)
    V = V[j]
    I = I[j]

    # adjust current for positive in reverse bias
    if I[0] < 0:
        I = -I


    ''' short circuit '''

    # calculate Isc from linear regression about -0.2 < V < 0.2
    j = np.where( (V > -0.2) & (V < 0.2) )
    slope, icept, r_value, p_value, std_err = linregress(V[j], I[j])
    Isc = icept


    ''' open circuit '''

    # calculate Voc from linear regression about -0.5 < I < 0.5
    j = np.where( (I >= -3) & (I <= 4) )
    slope, icept, r_value, p_value, std_err = linregress(I[j], V[j])
    Voc = icept


    ''' maximum power point '''

    # power in forward bias region
    j = np.where( (V < Voc) & (V > 0.) )
    P = I[j]*V[j]

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

    # b-pline fit around maximum power point (rel. current)
    spl = splrep( V[j][k], I[j][k], )

    # derivative of power at maximum power point current
    Impp = float( splev(Vmpp, spl) )

    # power at maximum power point
    Pmpp = Vmpp*Impp


    ''' solar performance '''

    # calculate fill factor
    FF = Pmpp/(Isc*Voc)

    # calculate solar conversion efficiency
    Eta = (Isc*Voc*FF)/A


    # pack data
    calc_params = {
        #'current': I,
        #'voltage': V,
        'area': A,
        'isc': Isc,
        'voc': Voc,
        'pmpp': Pmpp,
        'impp': Impp,
        'vmpp': Vmpp,
        'ff': FF,
        'eta': Eta,
    }


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

    V = _data['voltage']
    I = _data['current']

    # sort data on voltage (start low)
    j = np.argsort(V)
    V = V[j]
    I = I[j]

    # adjust current for positive in reverse bias
    if I[0] < 0:
        I = -I


    # filter for only low reverse bias region
    j = np.where( (V >= -5.) & (V <= -1.) )[0]
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


    V_f = _full_data['voltage']
    I_f = _full_data['current']

    # sort data on voltage (start low)
    j = np.argsort(V_f)
    V_f = V_f[j]
    I_f = I_f[j]

    # adjust current for positive in reverse bias
    if I_f[0] < 0:
        I_f = -I_f


    V_h = _half_data['voltage']
    I_h = _half_data['current']

    # sort data on voltage (start low)
    j = np.argsort(V_h)
    V_h = V_h[j]
    I_h = I_h[j]

    # adjust current for positive in reverse bias
    if I_h[0] < 0:
        I_h = -I_h


    # calculate Isc from linear regression about -0.2 < V < 0.2
    j = np.where( (V_f > -0.2) & (V_f < 0.2) )
    slope, icept, r_value, p_value, std_err = linregress(V_f[j], I_f[j])
    Isc_f = icept

    # calculate Isc from linear regression about -0.2 < V < 0.2
    j = np.where( (V_h > -0.2) & (V_h < 0.2) )
    slope, icept, r_value, p_value, std_err = linregress(V_h[j], I_h[j])
    Isc_h = icept


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


    if True:

        # current density
        results['jsc'] = (results['isc']) / results['area']
        results['jmpp'] = (results['impp']) / results['area']


        # calculate series adjusted area values [Ohm cm^2]
        results['rs_sqr'] = results['rs'] * results['area'] * 1e3
        results['rp_sqr'] = results['rp'] * results['area'] * 1e3

    if False:

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





''' convergence of series resistance
ref doi 10.1016/j.solener.2018.01.047


# thermal voltage
def Vt_(T):
    q = 1.602e-19 # [C]
    kB = 1.38e-23 # [J/K]
    return kB*T/q

# factor for relative diode saturation currents
def K_(T):
    return (T**(2/5)) / 3.77

# diode rectification at open circuit
def Xoc_(Voc, a, Vt):
    return np.exp(Voc/(a*Vt))

# diode rectification at maximum power point
def Xmpp_(Vmpp, Rs, Impp, a):
    return np.exp((Vmpp + Rs*Impp)/(a*Vt))

# diode rectification at short circuit
def Xsc_(Rs, Isc, a):
    return np.exp((Rs*Isc)/(a*Vt))

# first diode saturation current
def Is1_(Voc, Isc, Impp, Vmmp, Rs, Xmpp1, K, Xmpp2, Xoc1, Xoc2):
    return (Voc*(Isc - Impp) - Vmmp*Isc) / (Voc*(Xmpp1 + K*Xmpp2) - Vmpp*(Xoc1 + K*Xoc2))

# second diode saturation current
def Is2_(K, Is1):
    return K*Is1

# generation current under illumination
def Iph_(Voc, Impp, Is1, Xmpp1, K, Xmpp2, Vmpp, Xoc1, Xoc2):
    return (Voc*Impp + Is1*(Voc*(Xmpp1 + K*Xmpp2) - Vmpp*(Xoc1 - K*Xoc2))) / (Voc - Vmpp)

# shunt resistance
def Rsh_(Vmpp, Impp, Rs, Iph, Is1, Xmpp1, Is2, Xmpp2):
    return (Vmpp + Impp*Rs) / (Iph - Impp - Is1*(Xmpp1 - 1) - Is2*(Xmpp2 - 1))

# series resistance
def Rs_(Vmpp, Impp, Is1, a1, Vt, Xmpp1, Is2, a2, Xmpp2, Rsh):
    return (Vmpp/Impp) - (1/((Is1/(a1*Vt))*Xmpp1 + (Is2/(a2*Vt))*Xmpp2 + (1/Rsh)))






# define measurement conditions
#T = 298.15 # [K]

# thermal voltage
Vt = Vt_(T)

# factor for relative diode saturation currents
K = K_(T)

# define diode ideality factors
a1 = 1.26
a2 = 2.84

# set initial series resistance
Rs = 0.0


## iterate series resistance calculation until convergence
eps = 1e-5
dRs = 1.
while dRs > eps:

    #print('\n Initial Rs {:.4f}\n'.format(Rs))

    # update series resistance
    Rs += eps

    # diode rectification at open circuit
    Xoc1 = Xoc_(Voc, a1, Vt)
    Xoc2 = Xoc_(Voc, a2, Vt)

    #print('\tXoc1 {:.1e}'.format(Xoc1))
    #print('\tXoc2 {:.1e}'.format(Xoc2))

    # diode rectification at maximum power point
    Xmpp1 = Xmpp_(Vmpp, Rs, Impp, a1)
    Xmpp2 = Xmpp_(Vmpp, Rs, Impp, a2)

    #print('\tXmpp1 {:.1e}'.format(Xmpp1))
    #print('\tXmpp2 {:.1e}'.format(Xmpp2))

    # diode rectification at short circuit
    Xsc1 = Xsc_(Rs, Isc, a1)
    Xsc2 = Xsc_(Rs, Isc, a2)

    #print('\tXsc1 {:.1e}'.format(Xsc1))
    #print('\tXsc2 {:.1e}'.format(Xsc2))


    # first diode saturation current
    Is1 = Is1_(Voc, Isc, Impp, Vmpp, Rs, Xmpp1, K, Xmpp2, Xoc1, Xoc2)

    #print('\tIs1 {:.2e}'.format(Is1))

    # second diode saturation current
    Is2 = Is2_(K, Is1)

    #print('\tIs2 {:.2e}'.format(Is2))


    # generation current under illumination
    Iph = Iph_(Voc, Impp, Is1, Xmpp1, K, Xmpp2, Vmpp, Xoc1, Xoc2)

    #print('\tIph {:.2f}'.format(Iph))


    # shunt resistance
    Rsh = Rsh_(Vmpp, Impp, Rs, Iph, Is1, Xmpp1, Is2, Xmpp2)

    #print('\tRsh {:.3f}'.format(Rsh))


    # calculate updated series resistance
    _Rs = Rs_(Vmpp, Impp, Is1, a1, Vt, Xmpp1, Is2, a2, Xmpp2, Rsh)

    #print('Calculated Rs {:.4f}\n'.format(_Rs))

    # check for convergence
    dRs = Rs - _Rs

    #print('Rs {:.5f}, _Rs {:.5f}, dRs {:.1e}'.format(Rs, _Rs, dRs))

    # update series resistance
    #Rs = _Rs
    #Rs += eps


print('\nRs {:.4f}'.format(Rs))
print('Rsh {:.2f}'.format(Rsh))
print('Is1 {:.2e}'.format(Is1))
print('Is2 {:.2e}'.format(Is2))





'''
