
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


def type_loana(file_path):

    ''' Parse HALM Current-Voltage Format

        Import current-voltage measurement settings and data from a HALM format file

    # inputs
        _file_path (str): full filepath

    Returns:
        dict: extracted data and parameters
    '''

    res = {}

    for ff in ['lgt', 'drk', 'jv']:

        with open(file_path[:-3]+ff, 'r', encoding = 'iso-8859-1') as file:

            lines = file.readlines()

        results = {}

        head_ids = [ i for i in range(len(lines)) if lines[i].startswith('[') ]
        tail_ids = [ i for i in range(len(lines)) if lines[i].startswith('\n') ]
        seg_ids = list(zip(head_ids, tail_ids))

        for seg in seg_ids[:]:
            header = lines[seg[0]].strip('\n[]')
            results[header] = {}
            for j in range(seg[0]+1, seg[1]):
                val = lines[j].strip('\n').split('\t')
                results[header][val[0][:-1]] = val[1:]


        idx = [ i for i in range(len(lines)) if lines[i].startswith('**Data**') ][0] + 1
        data = np.array([ [ float(l) for l in lines[i].strip('\n').split('\t') ] for i in range(idx, len(lines)) ])

        results['data'] = data

        keep = ['Results']
        results = { k:v for k,v in results.items() if k in keep }

        #print(results)


        res = { **res, **{ '{}-{}'.format(ff,k):float(v[0]) for k,v in results['Results'].items() if k != 'Model' } }


    # return data dict
    return res



def loana(file_type, file_path, file_name):

    ''' Parse File

        Parse source data file of given format, run post parse processing, and return imported data

    Args:
        file_path (str): full file path including name with extension
        file_type (str): data file format information

    Returns:
        dict: parsed, processed data and parameters from file
    '''

    # HALM IV
    #if file_type == 'jv':
    if True:

        # import raw data from file
        data = type_loana(file_path = '{}/{}'.format(file_path, file_name))


    # return imported data
    return data
