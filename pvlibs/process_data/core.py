
''' Functions

Summary:
    This file contains

Example:
    Usage of

Todo:
    *
'''



''' Imports '''

# processing for sinton lifetime data
from .sinton_lifetime import process_sinton_lifetime

# processing for sinton lifetime data
from .sinton_suns_voc import process_sinton_suns_voc

# processing for current-voltage data
from .current_voltage import process_current_voltage

# modeling for processed sinton lifetime data
from .model_lifetime import model_lifetime

# processing for current-voltage data
from .quantum_efficiency import process_quantum_efficiency


# process sinton lifetime data
from .slt import slt

# model lifetime
from .mlt import mlt

# current-voltage
from .iv import iv


''' Core Data Processing Functions '''

def process_measurement_data(_db, _index, _process):

    ''' Process Measurement Data

        Process measurement data by type, incorporate required experimental / device parameters; processed measurement
        data calculation results

    Args:
        _db (dict): database instance
        _index (int): measurement node index within database instance measurement list
        _process (dict): measurement and process type details

    Returns:
        dict: processed measurement data calculation results
    '''

    # process sinton lifetime measurement data
    if _process['measurement'] == 'sinton_lifetime':

        # process measurement data node and return result data
        return process_sinton_lifetime(_db = _db, _index = _index, _process = _process)

    # process sinton suns-voc measurement data
    if _process['measurement'] == 'sinton_suns_voc':

        # process measurement data node and return result data
        return process_sinton_lifetime(_db = _db, _index = _index, _process = _process)


    # process sinton lifetime measurement data
    if _process['measurement'] == 'model_lifetime':

        # process measurement data node and return result data
        return model_lifetime(_db = _db, _index = _index, _process = _process)


    # process sinton lifetime measurement data
    if _process['measurement'] == 'current_voltage':

        # process measurement data node and return result data
        return process_current_voltage(_db = _db, _index = _index, _process = _process)


    # process sinton lifetime measurement data
    if _process['measurement'] == 'quantum_efficiency':

        # process measurement data node and return result data
        return process_quantum_efficiency(_db = _db, _index = _index, _process = _process)



def process_calc_results(_db, _index, _process):

    ''' Process Measurement Data

        Process measurement data by type, incorporate required experimental / device parameters; processed measurement
        data calculation results

    Args:
        _db (dict): database instance
        _index (int): measurement node index within database instance measurement list
        _process (dict): measurement and process type details

    Returns:
        dict: processed measurement data calculation results
    '''

    # process sinton lifetime measurement data
    if _process['type'] == 'model_lifetime':

        # process measurement data node and return result data
        return model_lifetime(_db = _db, _index = _index, _process = _process)






def process_data(meas_type, data):

    ''' Process Measurement Data

        Process measurement data by type, incorporate required experimental / device parameters; processed measurement
        data calculation results

    Args:
        db (dict): database instance

    Returns:
        dict: processed measurement data calculation results
    '''

    # process sinton lifetime measurement data
    if meas_type == 'slt':

        # process measurement data node and return result data
        results = slt(data = data)

    # model sinton lifetime measurement data
    if meas_type == 'mlt':

        # process measurement data node and return result data
        results = mlt(data = data)

    # process current-voltage measurement data
    if meas_type == 'iv':

        # process measurement data node and return result data
        results = iv(data = data)


    return results
