
''' Database Persistant Storage Functions

Summary:
    This file contains functions for persistant storage of database instances.

Example:
    Usage of

Todo:
    *
'''


''' Imports '''

# object filesystem storage
import pickle



''' Filesystem Storage Functions '''

def save_to_file(_data, _base_path, _file_name):

    '''Store Data

        store data in static file (binary Pickle format)

    Args:
        _data (obj): data to store
        _base_path (str): directory path to store file
        _file_name (str): name of file

    Returns:
        bool: True if success, else False

        data stored in binary pickle file at base path / file name
    '''

    # open binary file for writing
    with open('{}/{}'.format(_base_path, _file_name), 'wb') as file:

        # dump pickle of data storage array to file
        pickle.dump(_data, file)

    # return True on success
    return True



def load_from_file(_base_path, _file_name):

    '''Load Data

        load data from static file (binary Pickle format)

    Args:
        _base_path (str): directory path to file
        _file_name (str): name of file

    Returns:
        obj: loaded data object

        data loaded from binary pickle file at base path / file name
    '''

    # open binary file for reading
    with open('{}/{}'.format(_base_path, _file_name), 'rb') as file:

        # load pickled data storage array
        data = pickle.load(file)

        # return loaded data
        return data
