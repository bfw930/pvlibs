
''' Core Orchestration Protocols

Summary:
    This file contains

Example:
    Usage of

Todo:
    *
'''



''' Imports '''

# filesystem navigation, system, regex
import os, sys, glob, re


# database module
from . import database

# data import module
from . import data_import

# data processing module
from . import process_data

# general functions module
from . import general



''' Core Data Import and Processing Functions '''

def import_measurement_data_file(_db, _file_format, _file_path, _params):

    ''' Import Measurement Data File

        Import measurement data from source file given file name/path, file format (measurement, template, extension),
        file name parse string, and measurement parameters; store imported data, measurement parameters, and relation
        to device node by device_id parameter; add measurement node relation to device node by device_id parameter

        If device node by device_id parameter no found in device database list, generate and add blank device node

    Args:
        _db (dict): database instance
        _file_format (dict): measurement file format information
        _file_path (str): full file path of source file including file name and extension
        _params (dict): required measurement experimental and device parameters

    Returns:
        int: index of processed measurement node appended to referenced database instance
    '''

    # import data from file
    datas = data_import.parse_data_file( _file_path = _file_path, _format = _file_format )

    # iterate each measurement data element imported from file
    for label, data in datas.items():


        # search database device list by device_id parameter
        index = database.get_index_match_params(_db = _db, _type = 'device',
            _params = {'device_id': _params['device_id']})

        # if no match then to existing device node
        if len(index) == 0:

            print('device {} does not exist'.format(_params['device_id']))


            # return index of found device node
            return 0


        # if matched, take device index (first, ignore multiple matches)
        else:
            device_index = index[0]


        # search database device state list by device_state_id and device_id parameters
        index = database.get_index_hard_match_params(_db = _db, _type = 'device_state',
            _params = {'device_state_id': _params['device_state_id'], 'device_id': _params['device_id']})

        # if no match then to existing device node
        if len(index) == 0:

            print('device state {} does not exist for device {}'.format(_params['device_state_id'],
                _params['device_id']))


            # return index of found device node
            return 0


        # if matched, take device index (first, ignore multiple matches)
        else:
            device_state_index = index[0]


        # set measurement relations
        rels = {'device':[device_index], 'device_state':[device_state_index]}

        # set measurement parameters
        measure_params = {**_params, 'measurement_type': _file_format['measurement'],
            'device_state_id': _params['device_state_id'], 'device_id': _params['device_id']}

        # if label (multiple measurements imported from single file), add measurement subtype parameter
        measure_params = {**measure_params, 'measurement_subtype': label}


        # generate and add measurement node to database
        node_index = database.add_node(_db = _db, _type = 'measurement', _data = data, _params = measure_params,
            _rels = rels)


        # add relation to device node by type by index
        success = database.add_relation(_db = _db, _node_type = 'device', _node_index = device_index,
            _rels_type = 'measurement', _rels_index = node_index)

        # add relation to device state node by type by index
        success = database.add_relation(_db = _db, _node_type = 'device_state', _node_index = device_state_index,
            _rels_type = 'measurement', _rels_index = node_index)


    # return added measurement node index
    return node_index



def process_measurement_data(_db, _index, _process):

    ''' Process Measurement Data

        Run data processing by measurement type on measurement node and store results in database

    Args:
        _db (dict): database instance
        _index (int): measurement node index within database instance measurement list
        _process (dict): measurement and process type details

    Returns:
        int: index of processed measurement node appended to referenced database instance
    '''

    # process measurement data and return calculation results
    data = process_data.process_measurement_data(_db = _db, _index = _index, _process = _process)


    # get measurement node
    node = _db['measurement'][_index]

    # get device state node from measurement node relation
    device_state_index = node['rels']['device_state'][0]
    device_state = _db['device_state'][device_state_index]

    # get device node from measurement node relation
    device_index = node['rels']['device'][0]
    device = _db['device'][device_index]


    # define processed data node parameters, measurement type and default data process
    params = {'measurement_type': _process['measurement'], 'calc_process': _process['process'],
              'device_state_id': device_state['params']['device_state_id'],
              'device_id': device['params']['device_id'],
              }


    # define processed data node relations to measurement data node
    rels = {'measurement': [_index], 'device_state': [device_state_index],'device': [device_index]}


    # generate and add processed data node to database
    node_index = database.add_node(_db = _db, _type = 'calc_results', _data = data, _params = params, _rels = rels)


    # add relation to measurement node by type by index
    success = database.add_relation(_db = _db, _node_type = 'measurement', _node_index = _index,
        _rels_type = 'calc_results', _rels_index = node_index)

    # add relation to device state node by type by index
    success = database.add_relation(_db = _db, _node_type = 'device_state', _node_index = device_state_index,
        _rels_type = 'calc_results', _rels_index = node_index)

    # add relation to device node by type by index
    success = database.add_relation(_db = _db, _node_type = 'device', _node_index = device_index,
        _rels_type = 'calc_results', _rels_index = node_index)


    # return added processed data node index
    return node_index


####
def process_device_data(_db, _device_id, _process):

    ''' Process Device Data ### WIP ###

        Run data processing on measurement nodes by device id and process type, store results in database

    Args:
        _db (dict): database instance
        _index (int): measurement node index within database instance measurement list
        _measurement (str): measurement type

    Returns:
        int: index of processed measurement node appended to referenced database instance
    '''


    ### need to confirm general process results structure

    # process measurement data and return calculation results and label
    results = pvlibs.process_data.process_device_data(_db = db, _device_id = _device_id, _process = _process)


    # iterate each returned process result
    for label, data in results:

        # define processed data node parameters, measurement type and default data process
        params = {'process_type': _process, 'results_type': label}


    ### need to raise measurement search to here, get indicies to build relations

        # define processed data node relations to measurement data node
        rels = {'measurement': [_index]}


        # generate and add processed data node to database
        node_index = database.add_node(_db = _db, _type = 'processed_data', _data = data, _params = params, _rels = rels)


    ### iterate each related measurement and add relation to processed_data node

        # add relation to measurement node by type by index
        success = database.add_relation(_db = _db, _node_type = 'measurement', _node_index = _index,
            _rels_type = 'processed_data', _rels_index = node_index)


    ### also add relation to device node for processed_data node


    # return added processed data node index
    return node_index



''' Orchestration Protocols '''

def import_measurement_data_files(_db, _file_format, _base_path, _parse_string, _params):

    ''' Import Measurement Data Files

        Quick batch import source data files of given measurement and format within a directory; requires device_id
        and device_state_id parameters (either manual input or parsed from file name)

    Args:
        _db (dict): database instance
        _file_format (str): measurement file format
        _base_path (str): full path to directory containing file for processing
        _parse_string (str): regex parse string to extract parameters from file name
        _params (dict): required measurement experimental and device parameters

    Returns:
        dict: database instance containing imported measurement data and processed data nodes
    '''

    # get list files within directory
    files_list = [f for f in os.listdir(_base_path) if os.path.isfile(os.path.join(_base_path, f))]

    # filter files list for valid format by file extension
    files_list = [f for f in files_list if f.split('.')[-1] == _file_format['file_extension']]


    # store index of successful imports of measurement data
    indicies = []

    # iterate files and parse to import data
    for file_name in files_list:


        # extract experimental measurement parameters from filename
        filename_params = general.str_parse_params(_string = file_name, _parse_string = _parse_string)

        if filename_params is not None:

            # merge parameters
            params = {**_params, **filename_params, 'file_name': file_name}

            # build full file path
            file_path = '{}/{}'.format(_base_path, file_name)

            # parse each data file, store measurement node in database instance
            node_index = import_measurement_data_file(_db = _db, _file_format = _file_format, _file_path = file_path,
                _params = params)

            # upon success, store index of measurement data node within database measurement list
            indicies.append(node_index)

            print('successful import data from file: {}'.format(file_name))



def add_files(db, base_path, props):

    ''' Add File Reference to Database

        Given directory (str) and database instance (list), recursively search directory for files
        of given file extension (props); append properties (dict) to node

    Args:
        db (list): database instance as list of file nodes (dict)
        base_path (str): full directory path to search
        props (dict): file properties to store in file node

    Returns:
        (none): file node added to database instance
    '''

    # recursive directory search for all desired pl images
    file_paths =  glob.glob(base_path + '/**/*.' + props['file_ext'] , recursive = True)

    #print(file_paths)

    # iterate files
    for path in file_paths:

        # extract file names from matched file paths
        file_name = path.split('/')[-1:][0]

        # get directory paths, remove file name
        file_path = path[:-len(file_name)-1]

        # define new database node
        node = {**props, 'file_name': file_name, 'file_path': file_path}

        # store node in database
        db.append(node)
