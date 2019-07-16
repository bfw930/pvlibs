
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
import pandas as pd



''' ECV File Format Parse Functions '''

def parse_format_csv(_file_path):

    ''' Parse PV Measurements Data Format

        Import ECV measurement settings and data from a WaveLabs IV format file

    # inputs
        _file_path (str): full filepath

    Returns:
        dict: extracted data and parameters
    '''

    # import data from file
    _data = pd.read_csv(_file_path, skiprows = 28, index_col = False)


    data = {}

    # filter and store only depth and doping density data
    keep = {'Depth': 'depth', 'N(1/cm³)': 'doping_density'}

    for k,v in keep.items():
        data[v] = _data[k].values


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



def parse_ecv(_file_path, _format):

    ''' Parse File

        Parse source data file of given format, run post parse processing, and return imported data

    Args:
        _file_path (str): full file path including name with extension
        _format (dict): data file format information

    Returns:
        dict: parsed, processed data and parameters from file
    '''

    # PV Measurements, 140 TETB
    if _format['file_extension'] in ['csv', 'CSV']:

        # process raw data, format independent, return result
        return process_raw_data( parse_format_csv(_file_path) )
