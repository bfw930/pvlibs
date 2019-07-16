
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



''' Quantum Efficiency File Format Parse Functions '''

def parse_format_pvm(_file_path):

    ''' Parse PV Measurements Data Format

        Import quantum efficiency measurement settings and data from a WaveLabs IV format file

    # inputs
        _file_path (str): full filepath

    Returns:
        dict: extracted data and parameters
    '''

    _data = []

    # import data segments and headers from txt file, store in lists
    with open(_file_path, 'r', encoding = 'utf-8') as file:

        # iterate lines within file
        for line in file.readlines()[1:]:

            # split tab-delimited data
            l = line.split('\t')

            # select only valid data rows and store
            if len(l) == 9:
                _data.append([l[0], l[1]])

    # stack data lists as array
    _data = np.stack(_data).astype(np.float32)

    data = {}
    data['wavelength'] = _data[:,0]
    data['quantum_efficiency'] = _data[:,1]/100


    # return data dict
    return data



''' File Import and Processing Functions '''

def process_raw_data(_raw_data, _filter = False):

    ''' Process Raw Data

        Process raw data parsed from file, file format independent; perform calculations, filter for return only
        required data and parameters

    Args:
        _raw_data (dict): raw data parsed from file
        _filter (bool): filter processed raw data or return complete dataset

    Returns:
        dict: processed raw data
    '''

    # filter for only required data and parameters to return
    if _filter:
        # define list of required
        required = []
        # return processed data, filtered by required
        #return { key: value for key, value in _raw_data.items() if key in required }
        pass


    # return complete raw data
    return {'': _raw_data}



def parse_quantum_efficiency(_file_path, _format):

    ''' Parse File

        Parse source data file of given format, run post parse processing, and return imported data

    Args:
        _file_path (str): full file path including name with extension
        _format (dict): data file format information

    Returns:
        dict: parsed, processed data and parameters from file
    '''

    # PV Measurements, 140 TETB
    if _format['equipment'] == 'pvm':

        # process raw data, format independent, return result
        return process_raw_data( parse_format_pvm(_file_path) )
