
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
import pandas as pd

import os


# database search functions
from .. import database



''' Data Processing Functions '''

def process_quantum_efficiency(_db, _index, _process):

    ''' Process Quantum Efficiency

        Process external quantum efficiency and reflectance data, calculate internal quantum efficiency and loss

    Args:
        _db (dict): database instance
        _index (int): measurement node index within database instance measurement list
        _process (dict): measurement and process type details

    Returns:
        dict: calculated derivative data
    '''

    # get measurement data node
    measurement = _db['measurement'][_index]

    # get device_id from measurement relations
    device_id = _db['device'][ measurement['rels']['device'][0] ]['params']['device_id']


    # external quantum efficiency
    params = {'measurement_type': 'quantum_efficiency', 'device_id': device_id, 'qe_type': 'eqe'}
    index = database.get_index_hard_match_params(_db = _db, _type = 'measurement', _params = params)[0]
    measurement = _db['measurement'][index]

    wl = measurement['data']['wavelength']

    qe = measurement['data']['quantum_efficiency'] * _process['eqe_scale'] # scale qe to fix absolute calibration

    # trim to solar range only
    j = np.where( (wl >= 300) & (wl <= 1200) )

    wl = wl[j]
    qe = qe[j]


    # reflectance
    params = {'measurement_type': 'quantum_efficiency', 'device_id': device_id, 'qe_type': 'refl'}
    index = database.get_index_hard_match_params(_db = _db, _type = 'measurement', _params = params)[0]
    measurement = _db['measurement'][index]

    r_wl = refl = measurement['data']['wavelength']

    refl = measurement['data']['quantum_efficiency'] - _process['refl_shad'] # only finger shading adjusted

    # trim to solar range only
    j = np.where( (r_wl >= 300) & (r_wl <= 1200) )

    refl = refl[j]


    # calculate internal quantum efficiency and loss components
    iqe = qe * (1 + refl)

    # aggregate results
    results = {'wl': wl, 'eqe': qe, 'refl': refl, 'iqe': iqe}


    # perform loss analysis
    if _process['process'] == 'loss':

        # contact shading (average over cell area)
        shad = np.ones(wl.shape[0]) * _process['contact_shad']
        results['shad'] = shad

        # inverse of iqe as recombination loss
        rec = (1 - iqe) - ((1 - iqe) * refl) - ((1 - iqe) * shad)
        results['rec'] = rec

        # total expected loss with contact shading
        #loss = (1 - qe) + shad
        loss = shad + refl + rec
        results['loss'] = loss


        # get solar data (AM1.5G irradiance spectrum), resample solar power spectrum on iqe wl sampling
        sol = get_solar_spectrum()
        _sol = np.column_stack([sol['wl'], sol['glo']])
        k = np.where( (_sol[:,0] >= wl.min()) & (_sol[:,0] <= wl.max()) )[0]
        _sol = _sol[k]
        _sol_smpl = []
        dw = wl[1] - wl[0]
        for i in range(len(wl)):
            w = wl[i]
            k = np.where( (_sol[:,0] >= w-dw/2) & (_sol[:,0] < w+dw/2) )[0]
            _sol_smpl.append( np.mean(_sol[k,1]) )
        sol = np.array(_sol_smpl)

        psol = (sol / ((4.1357e-15 * 2.9979e8 * 1e9) / (0.1 * wl * dw)))


        results['sol_power'] = sol
        results['sol_density'] = psol


    # return calculated results
    return results



''' Auxilary Functions '''

def get_solar_spectrum():

    ''' Get Solar Spectrum

        Import, parse, process, and return air mass solar spectrum dataset

    Returns:
        dict: solar spectrum dataset
    '''

    # import air mass solar spectrum
    sol = pd.read_excel(os.path.dirname(__file__) + '/../data/' + 'solar-spec.xls', skiprows = 1)

    # extract each dataset
    sol_am0 = sol.iloc[:, -2:].values
    sol_ext = sol.iloc[:, [0,1]].values
    sol_g = sol.iloc[:, [0,2]].values
    sol_d = sol.iloc[:, [0,3]].values

    # trim wavelength range
    j = np.where( (sol_g[:,0] >= 250) & (sol_g[:,0] <= 1450) )[0]

    # save data in dict arrays
    data = {}
    data['wl'] = sol_g[j,0]
    data['ext'] = sol_ext[j,1]
    data['glo'] = sol_g[j,1]
    data['dir'] = sol_d[j,1]


    # return calculated results
    return data

