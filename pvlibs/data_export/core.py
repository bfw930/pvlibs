
''' Data Export Functions

Summary:
    This file contains functions to perform data aggregation / selection and export to csv type file, as well as
    enable the direct export of data nodes to csv type files with included node metadata.

Example:
    Usage of

Todo:
    *
'''



''' Imports '''

# data array handling
import numpy as np



''' Core Data Export Functions '''

def export_array_data(_data, _head, _units, _file_path):

    ''' Export Array Data to File

        Export array data to csv-type file with header labels

    Args:
        _data (np.array): data array for export
        _head (list): headers for data labels as list of str
        _file_path (str): full file path for export data file

    Returns:
        none: data exported to file
    '''

    # build headers csv string from provided headers list
    head = ','.join( [str(h) for h in _head] )
    units = ','.join( [str(u) for u in _units] )

    header = head + '\n' + units


    # export data array to file with provided headers
    np.savetxt(X = _data, delimiter = ',', fname = _file_path, header = header, fmt = '%s', comments = '')



''' Data Node Import / Export Functions '''

def export_data_node(_db, _node_index, _node_type, _file_path):

    ''' Export Data Node to File

        Export data node to csv-type file including node metadata sufficient for independent data node import

    Args:
        _db (dict): database instance
        _file_path (str): full file path to data node files for import

    Returns:
        none: data node exported to file
    '''

    ##

    ##



def import_data_node(_db, _file_path):

    ''' Import Data Node from File

        Import data node from csv-type and node metadata files produced by data node export function

    Args:
        _db (dict): database instance
        _file_path (str): full file path to data node files for import

    Returns:
        index (int): index of imported data node
    '''

    ##

    ##

