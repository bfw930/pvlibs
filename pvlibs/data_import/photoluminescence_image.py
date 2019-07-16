
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

# python image library
from PIL import Image

import glob



''' Photoluminescence Image File Format Parse Functions '''

def parse_format_tif(_file_path):

    ''' Parse Photoluminescence Image in TIF file format

        Import photoluminescence image data from BT Imaging tool in TIF file format

    Args:
        _file_path (str): full filepath

    Returns:
        dict: extracted data and parameters
    '''

    # import image data from tif file into np array
    image = np.array( Image.open(_file_path) )


    if False:
        # read test file for exposure value
        exp = pd.read_csv(_meas[0], encoding = 'iso-8859-1', delimiter = '\t')['Exposure Time (s)'].values[0]


    # return data dict
    return {'raw_image': image}



## File Import and Processing Functions

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
    return { '': _raw_data }



def parse_photoluminescence_image(_file_path, _format):

    ''' Parse File

        Parse source data file of given format, run post parse processing, and return imported data

    Args:
        _file_path (str): full file path including name with extension
        _format (dict): data file format information

    Returns:
        dict: parsed, processed data and parameters from file
    '''

    # Photoluminescence Image, BTi
    if _format['file_extension'] == 'tif':

        # process raw data, format independent, return result
        return process_raw_data( parse_format_tif(_file_path) )

