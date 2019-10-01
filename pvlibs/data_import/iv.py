
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

# data table handling
import pandas as pd


from operator import itemgetter
from itertools import groupby



''' Current-Voltage File Format Parse Functions '''

def type_halm(file_path):

    ''' Parse HALM Current-Voltage Format

        Import current-voltage measurement settings and data from a HALM format file

    # inputs
        _file_path (str): full filepath

    Returns:
        dict: extracted data and parameters
    '''

    # file extract storage
    _headers = []; _data = []

    # import data segments and headers from txt file, store in lists
    with open(file_path, 'r', encoding = 'iso-8859-1') as file:

        lines = file.readlines()
        # row numbers [header, data start, n rows] for data segments, iterate
        segs = [
            [12, 13, 199], # 1.0 suns IV
            [12, 217, 199], # 0.5 suns IV
            [434, 435, 100], # dark reverse bias IV
            [548, 549, 200], # shunt res
            [762, 763, 200], # series res
        ]
        for s in segs:
            head, start, rows = s
            _headers.append(lines[head])
            _data.append([ lines[i] for i in range(len(lines))[start:start+rows] ])

    # parse header string, discard Nr, split for (name, units) by column, store array
    for i in range(len(_headers)):
        _headers[i] = np.array([ [head[str.index(head, ']')+1:],
                                 head[str.index(head, '[')+1:str.index(head, ']')]]
                                for head in str.split(str.strip(_headers[i]), '\t')[1:] ])

    # parse data rows, discard Nr, split each column, parse to float else zero, store array
    chk = lambda s: str.isdigit(str.join('',[ c for c in s if c not in ['.', '-', '+'] ]))
    for i in range(len(_data)):
        _data[i] = np.stack([ [ float(v) if chk(v) else 0.
                               for v in str.split(str.strip(row), '\t')[1:] ]
                             for row in _data[i] ])

    names = ['full', 'half', 'dark', 'shunt', 'series']

    # store each data array in dict with header as key
    #data_entry = { _headers[i][0][0]:_data[i][:,:] for i in list(range(len(_headers))) }
    data_entry = { names[i]: { 'voltage': _data[i][:,6][::-1],
                               'current': -_data[i][:,7][::-1],
                               'intensity': _data[i][:,8][::-1], }
        for i in range(len(names)) }

    # return data dict
    return data_entry



def type_halm_500(file_path):

    ''' Parse HALM Current-Voltage Format

        Import current-voltage measurement settings and data from a HALM format file

    # inputs
        _file_path (str): full filepath

    Returns:
        dict: extracted data and parameters
    '''

    # file extract storage
    _headers = []; _data = []

    # import data segments and headers from txt file, store in lists
    with open(file_path, 'r', encoding = 'iso-8859-1') as file:

        lines = file.readlines()

    # get all lines with 11 tab delimited values
    rows = [ i for i in range(len(lines)) if len(lines[i].split('\t')) == 11 ]

    ranges = []
    # get row ranges where group by > 10 consecutive data rows
    for key, group in groupby(enumerate(rows), lambda i: i[0] - i[1]):
        group = list(map(itemgetter(1), group))
        ranges.append((group[0], group[-1]))
    ranges = [r for r in ranges if (r[1] - r[0]) > 10]

    # parse and label data
    labels = ['full', 'half', 'dark', 'shunt', 'series']
    data = {}
    for r in range(len(labels)):
        d = np.array([ np.array(lines[i].split('\t')[1:-1], dtype = np.float64)
                            for i in range(ranges[r][0] + 1, ranges[r][1])
                            if '#INF' not in lines[i]])[:,-3:][::-1,:]
        data[labels[r]] = {}
        data[labels[r]]['voltage'] = d[:,-3]
        data[labels[r]]['current'] = -d[:,-2]
        data[labels[r]]['intensity'] = d[:,-1]*1e-3
        #data[labels[r]] = d[:,:]


    # return data dict
    return data



def parse_format_wavelabs(file_path):

    ''' Parse WaveLabs Current-Voltage Format

        Import current-voltage measurement settings and data from a WaveLabs IV format file

    # inputs
        _file_path (str): full filepath

    Returns:
        dict: extracted data and parameters
    '''

    # read in 4 header rows, convert to numpy array, discard null 3rd row, discard first 3 columns
    jv_head = pd.read_excel(io = file_path, sheet_name = 'IV-Raw', header = None, nrows = 4).values[[0, 1, 3], 3:]

    # read raw jv data from file, convert to numpy array, skip 4 header rows, discard first 3 columns
    jv_raw = pd.read_excel(io = file_path, sheet_name = 'IV-Raw', header = None, skiprows = 4,
        index_col = None).values[:, 3:]


    # get index of data columns (discard null cols)
    jv_datas_mask = [ i-1 for i in range(jv_head.shape[1]+1) if i%3 != 0 ]

    # get data columns (discard null cols)
    jv_datas = jv_raw[:, jv_datas_mask].astype(np.float32)


    # get name of each data column pair
    jv_data_names = jv_head[1, jv_datas_mask[1::2]].astype(np.str)

    # get step name of each data column pair
    jv_data_steps = jv_head[0, jv_datas_mask[1::2]].astype(np.str)

    # get units of each data column
    jv_data_units = jv_head[2, jv_datas_mask].astype(np.str)


    # set new unit labels
    relabel = {'Current [A]':'current', 'E':'intensity', 'Voltage [V]':'voltage'}

    # iterate and update unit labels
    for i in range(len(jv_data_units)):
        if jv_data_units[i] in relabel.keys():
            jv_data_units[i] = relabel[ jv_data_units[i] ]


    # set new step labels
    relabel = {'1 sun': 'full', '1/2 sun': 'half', 'SunsVoc': 'suns_voc', 'UV light': 'uv', 'IR light': 'ir',
        'dark': 'dark'}

    # iterate and update unit labels
    for i in range(len(jv_data_steps)):
        if jv_data_steps[i] in relabel.keys():
            jv_data_steps[i] = relabel[ jv_data_steps[i] ]


    # initialise data storage dict
    data = {}

    # iterate steps
    for i in range(len(jv_datas[1])):

        # unpack data and headers
        _data = jv_datas[:,i]
        step = jv_data_steps[int(i/2)]
        name = jv_data_names[int(i/2)]
        unit = jv_data_units[i]

        # only keep raw current, voltage, intensity data for select steps
        if step in ['full', 'half', 'suns_voc', 'dark']:

            # only keep raw current, voltage, intensity data for select steps
            if (name in ['Raw IV Data', 'Intensity']) and (unit in ['current', 'voltage', 'intensity']):

                # add step to dict
                if not step in data.keys():
                    data[step] = {}

                # store data array in dict by units, strip tail nan
                data[step][unit] = _data[np.where( np.invert(np.isnan(_data)) )]

    # return data dict
    return data



def iv(file_type, file_path, file_name):

    ''' Parse File

        Parse source data file of given format, run post parse processing, and return imported data

    Args:
        file_path (str): full file path including name with extension
        file_type (str): data file format information

    Returns:
        dict: parsed, processed data and parameters from file
    '''

    # HALM IV
    if file_type == 'halm':

        # import raw data from file
        data = type_halm(file_path = '{}/{}'.format(file_path, file_name))

    if file_type == 'halm-500':

        # import raw data from file
        data = type_halm_500(file_path = '{}/{}'.format(file_path, file_name))

    # return imported data
    return data
