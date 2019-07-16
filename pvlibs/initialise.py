
''' Database Initialisation Protocols

Summary:
    This file contains initialisation protocols and the underlying functions for setting up a database instance for an
    experiment, including: experimental details, a list of all samples processed and measured with details of invariant
    sample parameters, and complete list of all sample states containing variable sample parameters altered during any
    processing stage.

    Each of the above ('experiment', 'sample', 'sample_state') are stored as separate class nodes, linked in the
    following structure: experiment to sample, sample to sample_state.

    Each measurement performed is represented by a 'measurement' class node, containing raw data and measurement
    parameters imported from a source data file, and is linked to a single 'sample_state' node.

    Data processing is performed using 'measurement' node data, creating a new node of node class 'processed_data', and
    is linked to a single 'sample_state' node, as well as all 'measurement' nodes that supplied data for the process.

Example:
    Usage of the initialisation protocols within for the initial setup of a database instance is as follows::

        # define database metadata as dict of key: value pairs (note all keys should use underscores in place of spaces)
        meta = {'author': 'John Snow', 'create_date'}

        db = init()

Todo:
    * fix above docstring to remove experiment node for now, may be implimented at later date
    * update and finalise above example usage docstring
    * have linked experiment (sub)node structure generated independently, then enable insertion into existing db
'''



''' Imports '''

# database module
from . import database



''' Core Database Initialisation Functions '''

def init_device(_db, _device_id, _params):

    ''' Initialise Device Nodes

        Initialise device node with parameters into database instance

    Args:
        _db (dict): database instance
        _device_id (str): unique device id
        _params (dict): required device parameters
    '''

    # search database process list by process_id parameter
    index = database.get_index_match_params(_db = _db, _type = 'device',
        _params = {'device_id': _device_id})

    # if device node with device_id already exists, return index
    if len(index) != 0:

        print('device_id {} already exists'.format(_device_id))


        # return index of found device node
        return index[0]


    # if no conflicting process_id found, generate process node
    else:

        # set device parameters
        params = {'device_id': _device_id, **_params}

        # generate empty device node with device id parameter, get device node index
        device_index = database.add_node(_db = _db, _type = 'device', _data = {}, _params = params, _rels = {})


        # return generated device index
        return device_index



def init_process(_db, _process_id, _params):

    ''' Initialise Device Nodes

        Initialise process node with parameters into database instance

    Args:
        _db (dict): database instance
        _process_id (str): unique process id
        _params (dict): required process parameters
    '''

    # search database process list by process_id parameter
    index = database.get_index_match_params(_db = _db, _type = 'process',
        _params = {'process_id': _process_id})

    # if process node with process_id already exists, return index
    if len(index) != 0:

        print('process_id {} already exists'.format(_process_id))


        # return index of found process node
        return index[0]


    # if no conflicting process_id found, generate process node
    else:

        # set process parameters
        params = {'process_id': _process_id, **_params}

        # generate empty process node with process id parameter, get process node index
        process_index = database.add_node(_db = _db, _type = 'process', _data = {}, _params = params, _rels = {})


        # return generated process index
        return process_index



def init_device_state(_db, _device_state_id, _device_id, _params, _processes):

    ''' Initialise Device State Node

        Initialise device state node with parameters into database instance

    Args:
        _db (dict): database instance
        _device_state_id (str): unique device state id
        _device_id (str): device id
        _params (dict): required device state parameters
    '''

    # search database device list by device_id parameter
    device_index = database.get_index_match_params(_db = _db, _type = 'device', _params = {'device_id': _device_id})


    # if no device exists, return error
    if len(device_index) == 0:

        print('no device {} found'.format(_device_id))


        # return index of conflicting device state
        return 0


    else:
        # select first match
        device_index = device_index[0]


    # get device_state relations for device
    device_state_rels = _db['device'][device_index]['rels']['device_state']

    # if device states exist
    if len(device_state_rels) != 0:

        # iterate each device state relation, check for conflicts
        for device_state_index in device_state_rels:

            # get device state and check for
            if _db['device_state'][device_state_index]['params']['device_state_id'] == _device_state_id:

                print('device state {} already exists for device {}'.format(_device_state_id, _device_id))


                # return index of conflicting device state
                return device_state_index



    # set device state parameters
    params = {'device_state_id': _device_state_id, **_params, 'device_id': _device_id}


    # define device state relationships
    rels = {'device': [device_index]}

    # iterate list of related processes by id
    process_rels = []
    for process_id in _processes:

        # get index of each processes
        process_index = database.get_index_match_params(_db = _db, _type = 'process',
        _params = {'process_id': process_id})

        # check process exists
        if len(process_index) == 0:

            print('no process {} found'.format(process_id))


            # return index of conflicting device state
            return 0

        # if found, add process index to device state process relations list
        else:
            process_rels.append(process_index[0])

    # add process relations list to device state relations
    rels = {**rels, 'process': process_rels}



    # generate empty device state node, get index
    device_state_index = database.add_node(_db = _db, _type = 'device_state', _data = {}, _params = params,
    _rels = rels)


    # add device state relationship to device node
    success = database.add_relation(_db = _db, _node_type = 'device', _node_index = device_index,
        _rels_type = 'device_state', _rels_index = device_state_index)


    # return generated device state index
    return device_state_index




''' Helper Database Initialisation Functions '''

def init_device_list(_db, _devices, _params):

    ''' Initialise Device Nodes

        Initialise list of device nodes with parameters into database instance

    Args:
        _db (dict): database instance
        _devices (list): list of devices by device id
        _params (dict): required device parameters
    '''

    # iterate each device by device id
    for device_id in _devices:

        # generate device node
        device_index = init_device(_db = _db, _device_id = device_id, _params = _params)



def init_device_state_list(_db, _device_state_id, _devices, _params, _processes):

    ''' Initialise Device State Nodes

        Initialise list of device state nodes with parameters into database instance

    Args:
        _db (dict): database instance
        _device_state_id (str): unique device state id
        _devices (list): list of devices by device id to generate state for
        _params (dict): required device state parameters
    '''

    # iterate each device by device id
    for device_id in _devices:

        # generate device state node
        device_state_index = init_device_state(_db = _db, _device_state_id = _device_state_id, _device_id = device_id,
            _params = _params, _processes = _processes)



def init():

    ''' Initialise Database

    Experimental initialisation protocol; generate database instance, populate with samples and processes, generate
    sample states, return database instance

    Todo:
        * include database metadata for experimental details
        * include sample list with details for initialisation
        * include process list with details for initialisation
        * generate sample states (initial and post each process)


    Returns:
        dict: database instance
    '''

    # generate database instance
    db = database.init_db()


    # return initialised database instance
    return db








def initialise(_meta, _experiment, _samples, _sample_states):

    ''' Initialise Database ### WIP ###

    Initialise database for an experiment using provided experiment, sample, and sample_state information. Each of the
    entries for these catagories (experiment, sample, sample_state) are required to contain an 'id' parameter, which
    will be used to link the respective information class nodes together. You should however also provide all
    parameters that will be required for data processing steps that are to be performed.

    Args:
        _meta (dict): database metadata
        _experiment (dict): experimental details
        _samples (dict): sample details (invariant parameters)
        _sample_states (dict): sample details for a given state (variable between experimental processing steps)

    Returns:
        dict: generated database instance containing initialised and linked information nodes
    '''

    # generate and return database instance
    return database.init_db()

