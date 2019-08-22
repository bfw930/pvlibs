
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

# smoothing filter for derivative
from scipy.signal import savgol_filter



''' Sinton Lifetime File Format Parse Functions '''

def type_xlsm(file_path):

    ''' Parse XLSM Workbook Format

        Import photoconductance measurement settings and data from a sinton lifetime xlsm workbook

    # inputs
        _file_path (str): full filepath

    Returns:
        dict: extracted data and parameters
    '''

    # load source data workbook
    wb = openpyxl.load_workbook(file_path, read_only = True)
    ## data_only = True

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



def type_ltr(file_path):

    ''' Parse LTR LabView File Format

        Import photoconductance measurement settings and data from a sinton lifetime ltr file

    # inputs
        file_path (str): full filepath

    Returns:
        dict: extracted data and parameters
    '''

    # open data file and extract lines
    lines = open(file_path, 'r', encoding = 'iso-8859-1').readlines()

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



def slt(file_type, file_path, file_name):

    ''' Parse File

        Parse source data file of given format, run post parse processing, and return imported data

    Args:
        file_path (str): full file path including name with extension
        file_type (str): data file format information

    Returns:
        dict: parsed, processed data and parameters from file
    '''

    # TIF Photoluminescence Image, BTi
    if file_type == 'ltr':

        # import raw data from file
        _raw_data = type_ltr(file_path = '{}/{}'.format(file_path, file_name))

    if file_type == 'xlsm':

        # import raw data from file
        _raw_data = type_xlsm(file_path = '{}/{}'.format(file_path, file_name))


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


    # use voltage transient derivatives to trim start and end, remove error values and noise
    if False:

        # select data range
        x = _raw_data['time'].copy()
        y = _raw_data['conductance'].copy()
        z = _raw_data['illumination'].copy()

        # strip error values at head and tail (time and noise floor)
        j = np.where( (x > 0.) & (y > 5e-4) )
        x = x[j]; y = y[j]; z = z[j]

        # calculate first derivative
        dy = savgol_filter(y, 15, 2, deriv = 1, mode = 'nearest')
        ddy = savgol_filter(y, 15, 2, deriv = 2, mode = 'nearest')

        # strip error values
        j = np.where( (y > 1e-3) & (dy > 0.) )[0]
        if len(j) > 0:
            x = x[(j[-1]+1):]
            y = y[(j[-1]+1):]
            z = z[(j[-1]+1):]
            dy = dy[(j[-1]+1):]
            ddy = ddy[(j[-1]+1):]

        k = np.where( (ddy == ddy.max()) )[0][0]
        j = np.where( (ddy < 0.) & (x < x[k]) )[0]
        if len(j) > 0:
            x = x[(j[-1]+1):]
            y = y[(j[-1]+1):]
            z = z[(j[-1]+1):]

        # update raw data
        _raw_data['time'] = x
        _raw_data['conductance'] = y
        _raw_data['illumination'] = z



    ## filter for only required data and parameters to return

    # define list of required
    required = ['time', 'conductance', 'illumination', 'dark_res']

    # return processed data, filtered by required
    data = { key: value for key, value in _raw_data.items() if key in required }


    # return imported data
    return data
