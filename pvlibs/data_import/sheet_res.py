
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

def parse_format_txt(_file_path):

    ''' Parse PV Measurements Data Format

        Import  measurement settings and data from

    # inputs
        _file_path (str): full filepath

    Returns:
        dict: extracted data and parameters
    '''


    _data = pd.read_csv(_file_path, skiprows = 18, index_col = False, header = None, sep = '\t')

    data = {}

    data['front'] = _data[2].values
    data['rear'] = _data[3].values


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



def parse_sheet_res(_file_path, _format):

    ''' Parse File

        Parse source data file of given format, run post parse processing, and return imported data

    Args:
        _file_path (str): full file path including name with extension
        _format (dict): data file format information

    Returns:
        dict: parsed, processed data and parameters from file
    '''


    if _format['file_extension'] in ['txt']:

        # process raw data, format independent, return result
        return process_raw_data( parse_format_txt(_file_path) )
