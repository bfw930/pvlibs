
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

# parse xlsm files
import openpyxl



''' Sinton Suns-Voc File Format Parse Functions '''

def parse_format_svr(_file_path):

    ''' Parse LTR LabView File Format

        Import photoconductance measurement settings and data from a sinton lifetime ltr file

    # inputs
        _file_path (str): full filepath

    Returns:
        dict: extracted data and parameters
    '''

    # open data file and extract lines
    lines = open(_file_path, 'r', encoding = 'iso-8859-1').readlines()

    # initialise data storage dict
    data_entry = {}

    # iterate lines
    for l in range(len(lines)):

        # extract time data
        if str.startswith( lines[l], 'Time = "<' ):
            data_entry['time'] = np.array( str.split( str.replace( str.strip(lines[l]) , '"', '') , ' ')[3:],
            dtype = np.float32)

        # extract reference cell voltage data
        if str.startswith( lines[l], 'Ref = "<' ):
            data_entry['ref_volt'] = np.array( str.split( str.replace( str.strip(lines[l]) , '"', '') , ' ')[3:],
            dtype = np.float32)

        # extract photovoltage data
        if str.startswith( lines[l], 'PC = "<' ):
            data_entry['photo_volt'] = np.array( str.split( str.replace( str.strip(lines[l]) , '"', '') , ' ')[3:],
            dtype = np.float32)

        # reference cell calibration value in V/sun
        if str.startswith( lines[l], 'Ref Cell  (V/sun)'):
            data_entry['ref_cell_cal'] = float( str.split( str.replace( str.strip(lines[l]) , '"', '') , ' ')[5:][0] )


    # return data dict
    return data_entry



''' File Import and Processing Functions '''

def process_raw_data(_raw_data, _filter = True):

    ''' Process Raw Data

        Process raw data parsed from file, file format independent; perform calculations, filter for return only
        required data and parameters

    Args:
        _raw_data (dict): raw data parsed from file
        _filter (bool): filter processed raw data or return complete dataset

    Returns:
        dict: processed raw data
    '''

    ## calculate illumination intensity and photoconductance (ref Sinton Instruments)

    # calculate photovoltage
    _raw_data['photovoltage'] = _raw_data['photo_volt']

    # calculate illumination intensity from ref cell voltage and calibration
    _raw_data['illumination'] = (_raw_data['ref_volt'] / _raw_data['ref_cell_cal']) * 0.038 / 1.602e-19


    # filter for only required data and parameters to return
    if _filter:

        # define list of required
        required = ['time', 'photovoltage', 'illumination']

        # return processed data, filtered by required
        return {'sinton_suns_voc': { key: value for key, value in _raw_data.items() if key in required } }


    # return complete raw data
    return {'': _raw_data}



def parse_sinton_suns_voc(_file_path, _format):

    ''' Parse File

        Parse source data file of given format, run post parse processing, and return imported data

    Args:
        _file_path (str): full file path including name with extension
        _format (str): data file format

    Returns:
        dict: parsed, processed data and parameters from file
    '''

    ## select file parse function by format

    # labview datafile
    if _format['file_extension'] == 'svr':
        raw_data = parse_format_svr(_file_path)


    # process raw data, format independent, return result
    return process_raw_data( raw_data )
