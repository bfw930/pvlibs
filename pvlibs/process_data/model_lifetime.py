
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

# optimisation functions
from scipy import optimize


# lifetime model functions
from . import models

# wafer property calculation functions
from .wafer import calc_wafer_intrinsic, calc_wafer_equilibrium

# charge density dependent calculation functions
from .charge_density import calc_wafer_nonequilibrium



''' Core Calculation Functions '''

def get_nd_dep(_dn, _T, _N_D, _N_A, _E_c_i, _E_v_i, _N_c_i, _N_v_i, _n_i, _n_i_0, _n_0, _p_0):

    ''' Get Charge Density Dependent Values

        Calculate charge density dependent values: non-equilibrium effective intrinsic carrier concentration, radiative
        recombination lifetime, Auger recombination lifetime

    Args:
        _dn (np.array): excess electron concentrations [ / cm^-3]
        _params (dict): required parameters for calculations
        _intr (dict): parameters returned from intrinsic calculations
        _equil (dict): parameters returned from equilibrium calculations

    Returns:
        results (dict): calculated non-equilibrium values

            n_i_eff (np.array): effective non-equilibrium intrinsic carrier densities [ / cm^3]
            tau_aug (np.array): auger recombination lifetime [ / s]
            tau_rad (np.array): radiative recombination lifetime [ / s]
            dn (np.array): excess charge carrier density [ / cm^-3]
    '''

    # initialise results storage list
    n_i_eff = []
    tau_rad = []
    tau_aug = []


    # iterate each charge density value
    for i in range(len(_dn)):

        # calculate non-equilibrium values
        n, p, _n_i_eff = calc_wafer_nonequilibrium(_T = _T, _N_D = _N_D, _N_A = _N_A, _E_c_i = _E_c_i, _E_v_i = _E_v_i,
                                              _N_c_i = _N_c_i, _N_v_i = _N_v_i, _n_i = _n_i, _n_i_0 = _n_i_0,
                                              _dn = _dn[i], _dp = _dn[i])


        # store calculated value
        n_i_eff.append( _n_i_eff )


        # calculate radiative recombination lifetime
        _tau_rad = models.calc_tau_rad(_dn = _dn[i], _n = n, _p = p, _n_i_eff = _n_i_eff, _T = _T)

        # store calculated value
        tau_rad.append( _tau_rad )


        # calculate auger recombination lifetime
        _tau_aug = models.calc_tau_aug(_dn = _dn[i], _n = n, _p = p, _n_0 = _n_0, _p_0 = _p_0, _n_i_eff = _n_i_eff,
                                      _T = _T)

        # store calculated value
        tau_aug.append( _tau_aug )


    # pack results lists into arrays
    n_i_eff = np.array(n_i_eff)
    tau_rad = np.array(tau_rad)
    tau_aug = np.array(tau_aug)


    # return calculated non-equilibrium effective intrinsic carrier concentration as array
    return n_i_eff, tau_rad, tau_aug



def calc_tau_eff(_opt_vars, _params, _data, _comps, _names):

    ''' Calculate Effective Carrier Lifetime

        Calculate effective carrier lifetime from model sum of component recombination lifetimes

    Args:
        _opt_vars (list): model component optimisation variables
        _params (dict): required parameters for calculations
        _data (dict): results from charge density dependent calculations
        _comps (list): list of model components
        _names (list): list of optimisation variable names

    Returns:
        rec (dict): each calculated recombination component in model, inc. effective lifetime
    '''

    # unpack required non-equilibrium data values
    dn = _data['dn']

    # renormalise optimisation variables
    _opt_vars = [ 10.**v for v in _opt_vars]

    # store recombination and effective lifetimes
    rec = {'dn': dn}


    # check for radiative model component
    if 'rad' in _comps:

        # unpack radiative recombinaiton lifetime data
        rec['tau_rad'] = _data['tau_rad']


    # check for auger model component
    if 'aug' in _comps:

        # unpack auger recombinaiton lifetime data
        rec['tau_aug'] = _data['tau_aug']


    # check for sdr model component
    if 'sdr' in _comps:

        # unpack required parameters
        N_M = _params['N_M']
        W = _params['W']

        n_i_eff = _data['n_i_eff']

        # unpack srh optimisation variables
        J_0 = _opt_vars[ [ i for i in range(len(_names)) if _names[i] == 'J_0' ][0] ]


        # calculate surface defect recombination lifetime
        rec['tau_sdr'] = models.calc_tau_sdr(_dn = dn, _J_0 = J_0, _N_M = N_M, _n_i_eff = n_i_eff, _W = W )


    # check for srh model component
    if 'srh' in _comps:

        # unpack required parameters
        N_M = _params['N_M']

        # unpack srh optimisation variables
        t_m0 = _opt_vars[ [ i for i in range(len(_names)) if _names[i] == 't_m0' ][0] ]
        t_M0 = _opt_vars[ [ i for i in range(len(_names)) if _names[i] == 't_M0' ][0] ]


        # calculate SRH recombination lifetime
        rec['tau_srh'] = models.calc_tau_srh(_dn = dn, _N_M = N_M, _t_m0 = t_m0, _t_M0 = t_M0)


    # calculate effective charge carrier lifetime from inverse sum all model component lifetimes
    rec['tau_eff'] = ( sum( [ tau**-1 for tau in rec.values() ] ) )**-1


    # return calculated recombination and effective lifetimes
    return rec



def get_residual(_opt_vars, _params, _data, _ref, _comps, _names):

    ''' Get Effective Lifetime Residual

        Calculate effective carrier lifetime from model and return residual relative to measured effective lifetime

    Args:
        _opt_vars (list): model component optimisation variables
        _params (dict): required parameters for calculations
        _data (dict): results from charge density dependent calculations
        _comps (list): list of model components
        _names (list): list of optimisation variable names

    Returns:
        np.array: effective lifetime residual
    '''

    # calculate effective lifetime
    rec = calc_tau_eff(_opt_vars = _opt_vars, _params = _params, _data = _data, _comps = _comps, _names = _names)

    # calculate residual
    residual = _ref - rec['tau_eff']


    # return calculated residual
    return residual



def fit_model(_model_params, _sample, _sample_state, _measurement, _results):

    ''' Fit Effective Lifetime Model to Measurement Data

        Calculate effective carrier lifetime from model and fit to measured effective lifetime using minimisation over
        model component parameters; return fit results and components

    Args:
        _model (str): chosen model to fit to data
        _sample (dict): sample data node
        _sample_state (dict): sample state data node
        _measurement (dict): measurement data node
        _results (dict): results data node

    Returns:
        dict: effective lifetime fit results and model components
    '''

    T = _measurement['params']['temperature']
    W = _sample_state['params']['wafer_thickness']
    N_D = _results['data']['N_D']
    N_A = _results['data']['N_A']
    N_M = np.max([N_D, N_A])

    # initialise global parameters storage dict
    params = {'T': T, 'W': W, 'N_M': N_M, 'N_D': N_D, 'N_A': N_A}


    # intrinsic calculation
    N_c_i, N_v_i, E_c_i, E_v_i, n_i = calc_wafer_intrinsic(_T = T)


    # calculate effective equilibrium parameters
    n_0, p_0, n_i_0 = calc_wafer_equilibrium(_T = T, _N_D = N_D, _N_A = N_A, _E_c_i = E_c_i, _E_v_i = E_v_i,
                                             _N_c_i = N_c_i, _N_v_i = N_v_i, _n_i = n_i)


    # unpack required data to fit model
    nd = _results['data']['nd']
    tau = _results['data']['tau']


    # trim charge density data range
    j = np.where((nd >= _model_params['nd_range'][0]) & (nd <= _model_params['nd_range'][1]))
    nd = nd[j]
    tau = tau[j]


    # get charge density dependent values (n_i_eff, tau_aug, tau_rad), assume equal excess electron, hole generation
    n_i_eff, tau_rad, tau_aug = get_nd_dep(_dn = nd, _T = T, _N_D = N_D, _N_A = N_A, _E_c_i = E_c_i, _E_v_i = E_v_i,
                                           _N_c_i = N_c_i, _N_v_i = N_v_i, _n_i = n_i, _n_i_0 = n_i_0, _n_0 = n_0,
                                           _p_0 = p_0)

    data = {'n_i_eff': n_i_eff, 'tau_rad': tau_rad, 'tau_aug': tau_aug, 'dn': nd}


    # select model to fit
    if _model_params['model'] == 'std':

        # define model, initial parameter values, parameter limits; (log values for parameters)
        model = {'aug':{}, 'rad':{},
                 'sdr':{'params':['J_0'],
                        'inits':[-14],
                        'limits':[ [-16, -11] ]},
                 'srh':{'params':['t_m0', 't_M0'],
                        'inits':[-5, -4],
                        'limits':[ [-7, -1], [-7, -1] ]},}

    if _model_params['model'] == 'sdr':

        # define model, initial parameter values, parameter limits; (log values for parameters)
        model = {'aug':{}, 'rad':{},
                 'sdr':{'params':['J_0'],
                        'inits':[-14],
                        'limits':[ [-16, -11] ]},}


    # prepare model and params for optimisation
    comps = [ k for k in model.keys() ]
    opt_vars = [ p for v in model.values() if len(v) != 0 for p in v['params'] ]
    inits = [ i for v in model.values() if len(v) != 0 for i in v['inits'] ]
    limits = [ l for v in model.values() if len(v) != 0 for l in v['limits'] ]
    bounds = [ tuple( l[i] for l in limits ) for i in range(len(limits[0])) ]


    # minimise using bounded nonlinear least-squares
    opt = optimize.least_squares(fun = get_residual, x0 = inits, bounds = bounds,
        args = (params, data, tau, comps, opt_vars), jac = '3-point',
        method = 'trf', ftol = 1e-10, xtol = 1e-12, gtol = 1e-12, x_scale = 'jac', loss = 'cauchy')


    # define new charge density range
    dn = np.logspace(13, 17, 100)

    # get charge density dependent values (n_i_eff, tau_aug, tau_rad), assume equal excess electron, hole generation
    n_i_eff, tau_rad, tau_aug = get_nd_dep(_dn = dn, _T = T, _N_D = N_D, _N_A = N_A, _E_c_i = E_c_i, _E_v_i = E_v_i,
                                           _N_c_i = N_c_i, _N_v_i = N_v_i, _n_i = n_i, _n_i_0 = n_i_0, _n_0 = n_0,
                                           _p_0 = p_0)

    data = {'n_i_eff': n_i_eff, 'tau_rad': tau_rad, 'tau_aug': tau_aug, 'dn': dn}


    # calculate sdr, srh, and effective charge carrier lifetime from optimal parameters
    rec = calc_tau_eff(_opt_vars = opt.x, _params = params, _data = data, _comps = comps, _names = opt_vars)


    # calculate bulk lifetime component
    rec['tau_blk'] = (rec['tau_eff']**-1 - rec['tau_sdr']**-1)**-1


    # store optimal model parameters
    rec['opt_vars'] = { opt_vars[i]: np.power(10., opt.x[i]) for i in range(len(opt_vars)) }


    # calculate and store values
    rec['J_0'] = rec['opt_vars']['J_0']
    rec['t_blk'] = rec['tau_blk'].max()
    rec['t_eff'] = rec['tau_eff'].max()


    # store model used for calculations
    rec['model'] = _model_params['model']
    rec['residual'] = opt.fun


    # residual sum of squares
    ss_res = np.sum((opt.fun) ** 2)

    # total sum of squares
    ss_tot = np.sum((tau - np.mean(tau)) ** 2)

    # r-squared
    r2 = 1 - (ss_res / ss_tot)


    rec['R2'] = r2
    rec['ttt'] = tau


    # return fitting results
    return rec



def model_lifetime(_db, _index, _process):

    ''' Model Lifetime Data

        Model lifetime data from calculation results node, return model results

    Args:
        _db (dict): database instance
        _index (int): measurement node index within database instance measurement list
        _process (dict): measurement and process type details

    Returns:
        dict: effective lifetime fit results and model components
    '''

    # get model parameters
    model_params = _process['model_params']


    # get calculation results data node
    results = _db['calc_results'][_index]

    # get required related data nodes
    measurement = _db['measurement'][ results['rels']['measurement'][0] ]
    device_state = _db['device_state'][ results['rels']['device_state'][0] ]
    device = _db['device'][ results['rels']['device'][0] ]


    # perform lifetime modeling and return results
    fit = fit_model(_model_params = model_params, _sample = device, _sample_state = device_state,
                    _measurement = measurement, _results = results)


    # return model fitting results
    return fit



def sim_model(_model_params, _sample, _sample_state, _measurement, _results):

    ''' Fit Effective Lifetime Model to Measurement Data

        Calculate effective carrier lifetime from model and fit to measured effective lifetime using minimisation over
        model component parameters; return fit results and components

    Args:
        _model (str): chosen model to fit to data
        _sample (dict): sample data node
        _sample_state (dict): sample state data node
        _measurement (dict): measurement data node
        _results (dict): results data node

    Returns:
        dict: effective lifetime fit results and model components
    '''

    T = _measurement['params']['temperature']
    W = _sample_state['params']['wafer_thickness']
    N_D = _results['data']['N_D']
    N_A = _results['data']['N_A']
    N_M = np.max([N_D, N_A])

    # initialise global parameters storage dict
    params = {'T': T, 'W': W, 'N_M': N_M, 'N_D': N_D, 'N_A': N_A}


    # intrinsic calculation
    N_c_i, N_v_i, E_c_i, E_v_i, n_i = calc_wafer_intrinsic(_T = T)


    # calculate effective equilibrium parameters
    n_0, p_0, n_i_0 = calc_wafer_equilibrium(_T = T, _N_D = N_D, _N_A = N_A, _E_c_i = E_c_i, _E_v_i = E_v_i,
                                             _N_c_i = N_c_i, _N_v_i = N_v_i, _n_i = n_i)


    # define new charge density range
    dn = np.logspace(13, 17, 100)

    # get charge density dependent values (n_i_eff, tau_aug, tau_rad), assume equal excess electron, hole generation
    n_i_eff, tau_rad, tau_aug = get_nd_dep(_dn = dn, _T = T, _N_D = N_D, _N_A = N_A, _E_c_i = E_c_i, _E_v_i = E_v_i,
                                           _N_c_i = N_c_i, _N_v_i = N_v_i, _n_i = n_i, _n_i_0 = n_i_0, _n_0 = n_0,
                                           _p_0 = p_0)

    data = {'n_i_eff': n_i_eff, 'tau_rad': tau_rad, 'tau_aug': tau_aug, 'dn': dn}


    # define model, initial parameter values, parameter limits; (log values for parameters)
    model = _model_params['model_params']


    comps = [ k for k in model.keys() ]
    inits = [ np.log10(i) for v in model.values() if len(v) != 0 for i in v['inits'] ]
    opt_vars = [ p for v in model.values() if len(v) != 0 for p in v['params'] ]


    # calculate sdr, srh, and effective charge carrier lifetime from optimal parameters
    rec = calc_tau_eff(_opt_vars = inits, _params = params, _data = data, _comps = comps, _names = opt_vars)


    # calculate bulk lifetime component
    rec['tau_blk'] = (rec['tau_eff']**-1 - rec['tau_sdr']**-1)**-1


    # store optimal model parameters
    rec['opt_vars'] = { opt_vars[i]: np.power(10., inits[i]) for i in range(len(inits)) }


    # calculate and store values
    rec['J_0'] = rec['opt_vars']['J_0']
    rec['t_blk'] = rec['tau_blk'].max()
    rec['t_eff'] = rec['tau_eff'].max()


    # store model used for calculations
    rec['model'] = _model_params['model']


    # return fitting results
    return rec




def quick_fit_model(model, params, data):

    ''' Fit Effective Lifetime Model to Measurement Data

        Calculate effective carrier lifetime from model and fit to measured effective lifetime using minimisation over
        model component parameters; return fit results and components

    Args:
        _model (str): chosen model to fit to data
        _sample (dict): sample data node
        _sample_state (dict): sample state data node
        _measurement (dict): measurement data node
        _results (dict): results data node

    Returns:
        dict: effective lifetime fit results and model components
    '''

    T = params['temperature']
    W = params['wafer_thickness']
    N_D = data['N_D']
    N_A = data['N_A']
    N_M = np.max([N_D, N_A])

    # initialise global parameters storage dict
    params = {'T': T, 'W': W, 'N_M': N_M, 'N_D': N_D, 'N_A': N_A}


    # intrinsic calculation
    N_c_i, N_v_i, E_c_i, E_v_i, n_i = calc_wafer_intrinsic(_T = T)


    # calculate effective equilibrium parameters
    n_0, p_0, n_i_0 = calc_wafer_equilibrium(_T = T, _N_D = N_D, _N_A = N_A, _E_c_i = E_c_i, _E_v_i = E_v_i,
                                             _N_c_i = N_c_i, _N_v_i = N_v_i, _n_i = n_i)


    # unpack required data to fit model
    nd = data['nd']
    tau = data['tau']


    # trim charge density data range
    j = np.where((nd >= model['nd_range'][0]) & (nd <= model['nd_range'][1]))
    nd = nd[j]
    tau = tau[j]


    # get charge density dependent values (n_i_eff, tau_aug, tau_rad), assume equal excess electron, hole generation
    n_i_eff, tau_rad, tau_aug = get_nd_dep(_dn = nd, _T = T, _N_D = N_D, _N_A = N_A, _E_c_i = E_c_i, _E_v_i = E_v_i,
                                           _N_c_i = N_c_i, _N_v_i = N_v_i, _n_i = n_i, _n_i_0 = n_i_0, _n_0 = n_0,
                                           _p_0 = p_0)

    data = {'n_i_eff': n_i_eff, 'tau_rad': tau_rad, 'tau_aug': tau_aug, 'dn': nd}


    # define model, initial parameter values, parameter limits; (log values for parameters)
    model = {'aug':{}, 'rad':{},
             'sdr':{'params':['J_0'],
                    'inits':[-14],
                    'limits':[ [-16, -11] ]},
             'srh':{'params':['t_m0', 't_M0'],
                    'inits':[-5, -4],
                    'limits':[ [-7, -1], [-7, -1] ]},}


    # prepare model and params for optimisation
    comps = [ k for k in model.keys() ]
    opt_vars = [ p for v in model.values() if len(v) != 0 for p in v['params'] ]
    inits = [ i for v in model.values() if len(v) != 0 for i in v['inits'] ]
    limits = [ l for v in model.values() if len(v) != 0 for l in v['limits'] ]
    bounds = [ tuple( l[i] for l in limits ) for i in range(len(limits[0])) ]


    # minimise using bounded nonlinear least-squares
    opt = optimize.least_squares(fun = get_residual, x0 = inits, bounds = bounds,
        args = (params, data, tau, comps, opt_vars), jac = '3-point',
        method = 'trf', ftol = 1e-10, xtol = 1e-12, gtol = 1e-12, x_scale = 'jac', loss = 'cauchy')


    # define new charge density range
    dn = np.logspace(13, 17, 100)

    # get charge density dependent values (n_i_eff, tau_aug, tau_rad), assume equal excess electron, hole generation
    n_i_eff, tau_rad, tau_aug = get_nd_dep(_dn = dn, _T = T, _N_D = N_D, _N_A = N_A, _E_c_i = E_c_i, _E_v_i = E_v_i,
                                           _N_c_i = N_c_i, _N_v_i = N_v_i, _n_i = n_i, _n_i_0 = n_i_0, _n_0 = n_0,
                                           _p_0 = p_0)

    data = {'n_i_eff': n_i_eff, 'tau_rad': tau_rad, 'tau_aug': tau_aug, 'dn': dn}


    # calculate sdr, srh, and effective charge carrier lifetime from optimal parameters
    rec = calc_tau_eff(_opt_vars = opt.x, _params = params, _data = data, _comps = comps, _names = opt_vars)


    # calculate bulk lifetime component
    rec['tau_blk'] = (rec['tau_eff']**-1 - rec['tau_sdr']**-1)**-1


    # store optimal model parameters
    rec['opt_vars'] = { opt_vars[i]: np.power(10., opt.x[i]) for i in range(len(opt_vars)) }


    # calculate and store values
    rec['J_0'] = rec['opt_vars']['J_0']
    rec['t_blk'] = rec['tau_blk'].max()
    rec['t_eff'] = rec['tau_eff'].max()


    # return fitting results
    return rec
