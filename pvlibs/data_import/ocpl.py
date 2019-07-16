
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

# python image library
from PIL import Image



''' Parse Functions '''

def type_tif(file_path):

    ''' Parse Photoluminescence Image in TIF file format

        Import photoluminescence image data from BT Imaging tool in TIF file format

    Args:
        _file_path (str): full filepath

    Returns:
        dict: extracted data and parameters
    '''

    # import image data from tif file into np array, return data dict
    return {'raw_img': np.array( Image.open(file_path) )}


def type_tif(file_path):

    ''' Parse Photoluminescence Image in TIF file format

        Import photoluminescence image data from BT Imaging tool in TIF file format

    Args:
        _file_path (str): full filepath

    Returns:
        dict: extracted data and parameters
    '''

    # import image data from tif file into np array, return data dict
    return {'raw_img': np.array( Image.open(file_path) )}



def ocpl(file_type, file_path, file_name):

    ''' Parse File

        Parse source data file of given format, run post parse processing, and return imported data

    Args:
        file_path (str): full file path including name with extension
        file_type (str): data file format information

    Returns:
        dict: parsed, processed data and parameters from file
    '''

    # TIF Photoluminescence Image, BTi
    if file_type == 'tif':

        # import raw data from file
        data = type_tif(file_path = '{}/{}'.format(file_path, file_name))


    try:
        # read measurement settings file
        sett = pd.read_csv('{}/meas_wafer_upl.txt'.format(file_path),
            encoding = 'iso-8859-1', delimiter = '\t')

        # extract exposure value matched by file id
        data['exposure'] = sett[sett['id'] == int(file_name[:5])]['Exposure Time (s)'].values[0]
        data['intensity'] = sett[sett['id'] == int(file_name[:5])].iloc[:,31].values[0]/2.5e17


    except:
        # no measurement properties file
        pass


    try:
        # read measurement settings file
        sett = pd.read_csv('{}/meas_cell_ploc.txt'.format(file_path),
            encoding = 'iso-8859-1', delimiter = '\t')

        # extract exposure value matched by file id
        data['exposure'] = sett[sett['id'] == int(file_name[:5])]['Exposure Time (s)'].values[0]
        data['intensity'] = sett[sett['id'] == int(file_name[:5])].iloc[:,31].values[0]/2.5e17


    except:
        # no measurement properties file
        pass


    try:
        # read measurement settings file
        sett = pd.read_csv('{}/meas_cell_ploc.txt'.format(file_path),
            encoding = 'iso-8859-1', delimiter = '\t')

        # extract exposure value matched by file id
        data['exposure'] = sett[sett['id'] == int(file_name[:6])]['Exposure Time (s)'].values[0]
        data['intensity'] = sett[sett['id'] == int(file_name[:6])].iloc[:,36].values[0]/2.5e17


    except:
        # no measurement properties file
        pass



    # return imported data
    return data

