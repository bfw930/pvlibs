
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



''' Sinton Lifetime File Format Parse Functions '''

def parse_format_xlsm(_file_path):

    ''' Parse XLSM Workbook Format

        Import photoconductance measurement settings and data from a sinton lifetime xlsm workbook

    # inputs
        _file_path (str): full filepath

    Returns:
        dict: extracted data and parameters
    '''

    # load source data workbook
    wb = openpyxl.load_workbook(_file_path, read_only = True)

    # load worksheets from workbook
    ws_calc = wb['Calc']
    ws_settings = wb['Settings']
    ws_user = wb['User']

    # initialise data storage dict
    data_entry = {}

    ## extract raw photoconductance data (photovoltage and ref cell voltage)

    data_entry['time'] = np.array([ c[0].value for c in ws_calc['A9:A133'] ], dtype = np.float32)
    data_entry['photo_volt'] = np.array([ c[0].value for c in ws_calc['B9:B133'] ], dtype = np.float32)
    data_entry['ref_volt'] = np.array([ c[0].value for c in ws_calc['C9:C133'] ], dtype = np.float32)

    ## extract additional source parameters from worksheets

    # reference cell calibration value in V/sun
    data_entry['ref_cell_cal'] = ws_settings['C5'].value

    # dark voltage
    data_entry['dark_volt'] = ws_calc['B166'].value

    # instrument calibration values
    data_entry['instr_cal_a'] = ws_settings['C6'].value
    data_entry['instr_cal_b'] = ws_settings['C7'].value
    data_entry['instr_offset'] = ws_settings['C8'].value
    data_entry['instr_air_volt'] = np.mean([ ws_settings['O{}'.format(cell)].value for cell in range(4, 13) ])

    # return data dict
    return data_entry



def parse_format_ltr(_file_path):

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

        # dark voltage value
        if str.startswith( lines[l], 'Vdark'):
            data_entry['dark_volt'] = float( str.split( str.replace( str.strip(lines[l]) , '"', '') , ' ')[2:][0] )

        # reference cell calibration value in V/sun
        if str.startswith( lines[l], 'Ref Cell  (V/sun)'):
            data_entry['ref_cell_cal'] = float( str.split( str.replace( str.strip(lines[l]) , '"', '') , ' ')[5:][0] )

        # average air voltage calibration value
        if str.startswith( lines[l], 'Avg. Air Voltage'):
            data_entry['instr_air_volt'] = float( str.split( str.replace( str.strip(lines[l]) , '"', '') , ' ')[4:][0] )

        # instrument calibration values
        if str.startswith( lines[l], 'A = "'):
            data_entry['instr_cal_a'] = float( str.split( str.replace( str.strip(lines[l]) , '"', '') , ' ')[2:][0] )
        if str.startswith( lines[l], 'B = "'):
            data_entry['instr_cal_b'] = float( str.split( str.replace( str.strip(lines[l]) , '"', '') , ' ')[2:][0] )
        if str.startswith( lines[l], 'Offset'):

            #data_entry['instr_offset'] = float( str.split( str.replace( str.strip(lines[l]) , '"', '') , ' ')[5:][0] )
            data_entry['instr_offset'] = float(str.split(lines[l], '"')[-2])

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

    # calculate instrument calibration value
    instr_cal_c = _raw_data['instr_air_volt'] - _raw_data['instr_offset']

    # calculate dark conductance
    dark_cond = (_raw_data['dark_volt'] - instr_cal_c) * (_raw_data['instr_cal_a'] * (_raw_data['dark_volt'] -
        instr_cal_c) + _raw_data['instr_cal_b'])

    # calculate illuminated conductance
    photo_cond = ( (_raw_data['photo_volt'] + _raw_data['dark_volt'] - instr_cal_c) * (_raw_data['instr_cal_a'] *
        (_raw_data['photo_volt'] + _raw_data['dark_volt'] - instr_cal_c) + _raw_data['instr_cal_b']) )

    # calculate net photoinduced conductance
    _raw_data['conductance'] = photo_cond - dark_cond

    # calculate illumination intensity from ref cell voltage and calibration
    _raw_data['illumination'] = (_raw_data['ref_volt'] / _raw_data['ref_cell_cal']) * 0.038 / 1.602e-19


    # calc dark sheet resistance
    _raw_data['dark_res'] = ( dark_cond )**-1


    # filter for only required data and parameters to return
    if _filter:

        # define list of required
        required = ['time', 'conductance', 'illumination', 'dark_res']

        # return processed data, filtered by required
        return {'sinton_lifetime': { key: value for key, value in _raw_data.items() if key in required } }


    # return complete raw data
    return {'': _raw_data}



def parse_sinton_lifetime(_file_path, _format):

    ''' Parse File

        Parse source data file of given format, run post parse processing, and return imported data

    Args:
        _file_path (str): full file path including name with extension
        _format (str): data file format

    Returns:
        dict: parsed, processed data and parameters from file
    '''

    ## select file parse function by format

    # xlsm workbook
    if _format['file_extension'] == 'xlsm':
        raw_data = parse_format_xlsm(_file_path)

    # labview datafile
    if _format['file_extension'] == 'ltr':
        raw_data = parse_format_ltr(_file_path)


    # process raw data, format independent, return result
    return process_raw_data( raw_data )
