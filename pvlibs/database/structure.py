
''' Database Structure Definitions and Generation Functions

Summary:
    This file contains

Example:
    Usage of

Todo:
    *
'''



''' Imports '''



''' Database Structure Class Definitions '''

def class_db(_type):

    ''' Database Data Class

        Define database data structure by type

        meta: database metadata

    Args:
        _type (str): database type (default, not yet implimented)

    Returns:
        dict: database structure
    '''

    # default
    if _type == 'default':

        # define and return structure
        return {'meta': ['name', 'version'],
                'device': [],
                'process': [],
                'device_state': [],
                'measurement': [],
                'processed_data': []}



def class_node(_type):

    ''' Data Node Class

        Define data node structure by type; each node parameters, data, relations

        params: node headers, static
        rels: indicies of related data nodes
        data: node type specific data

    Args:
        _type (str): data node type

    Returns:
        dict: data node structure
    '''

    # measurement data node
    if _type == 'measurement':

        # define and return structure
        return {'params': ['measurement_type', 'datetime', 'operator', 'device_region'],
                'rels': ['device_state'],
                'data': []}


    # measurement data node
    if _type == 'device':

        # define and return structure
        return {'params': ['device_id'],
                'rels': ['experiment', 'device_state'],
                'data': []}


    # measurement data node
    if _type == 'device_state':

        # define and return structure
        return {'params': ['device_state_id'],
                'rels': ['device', 'measurement'],
                'data': []}


    # measurement data node
    if _type == 'process':

        # define and return structure
        return {'params': ['process_id'],
                'rels': ['experiment'],
                'data': []}


    # processed measurement data node
    if _type == 'calc_results':

        # define and return structure
        return {'params': ['calc_process'],
                'rels': ['measurement', 'device', 'device_state', 'process'],
                'data': []}



''' Database Structure Generation Functions '''

def join_req_add_params(_req, _add, _blank = 'str'):

    ''' Join Required and Additional Parameters

        Return single dict of joined required and additional parameter dists, using required params within additional
        where supplied, else blank required field

    Args:
        _req (dict): list of required parameters
        _add (dict): list of additional parameters, including values for required parameters where available

    Returns:
        dict: joined required and additional paramters

    '''

    if _blank == 'str':

        # build list of req fields using values passed in add, blank for missing
        req = { key:_add[key] if key in _add.keys() else '' for key in _req }

    elif _blank == 'list':

        # build list of req fields using values passed in add, blank for missing
        req = { key:_add[key] if key in _add.keys() else [] for key in _req }

    # build list of add fields not in req
    add = { key:value for key, value in _add.items() if key not in req.keys() }

    # return joined dicts
    return { **req, **add }



def gen_db(_type, _meta = {}):

    ''' Generate Database

    Args:
        _type (str): database type (not yet implimented)
        _meta (dict): - database metadata

    Returns:
        dict: generated database
    '''

    # get required structure
    required = class_db(_type = _type)


    # build metadata
    meta = join_req_add_params(_req = required['meta'], _add = _meta)


    # return generated database
    return {'meta': meta, **{ key: value for key, value in required.items() if key != 'meta' } }



def gen_node(_type, _params = {}, _rels = {}, _data = {}):

    ''' Generate Node

        generate data node; return blank template of required fields if only node type passed

    Args:
        _type (str): type of data node
        _params - data node parameters
        _relations - data node relations
        _data - data node data

    Returns:
        dict: generated data node
    '''

    # get node required defaults by type
    required = class_node(_type = _type)


    # build parameters
    params = join_req_add_params(_req = required['params'], _add = _params)

    # build relations
    rels = join_req_add_params(_req = required['rels'], _add = _rels, _blank = 'list')

    # build data
    data = join_req_add_params(_req = required['data'], _add = _data)


    # return generated node data structure
    return {'params': params, 'rels': rels, 'data': data}
