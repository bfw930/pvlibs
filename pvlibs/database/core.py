
''' Core Database Functions

Summary:
    This file contains

Example:
    Usage of

Todo:
    *
'''



''' Imports '''

# database structure and component generation
from .structure import gen_db, gen_node



''' Database Management Functions '''

def init_db(_type = 'default', _meta = {}):

    ''' Initialise Database

        Generate database with defaults

    Args:
        _type (str): type of database, default (not yet implimented)
        _meta (dict): database metadata

    Returns:
        dict: generated database
    '''

    # generate and return database
    return gen_db(_type = _type, _meta = _meta)



def add_node(_db, _type, _params = {}, _rels = {}, _data = {}):

    ''' Add Node

        Generate node by type and add to database

    Args:
        _db (dict): database instance
        _type (str): type of data node
        _params (dict): node parameters
        _rels (dict): node relations
        _data (dict): node data

    Returns:
        int: index of added node within node type list of database
    '''

    # generate node of given type using supplied content
    node = gen_node(_type = _type, _params = _params, _rels = _rels, _data = _data)


    ## add node to database instance by type

    # ensure node type list exists, else create
    if _type not in _db.keys():
        _db[_type] = []

    # append node to specific node type list
    _db[_type].append(node)

    # return index of added node
    return (len(_db[_type])-1)



def remove_node(_db, _type, _index):

    ''' Remove Node

        Remove a node by type and index from database

    Args:
        _db (dict): database instance
        _type (str): type of data node
        _index (int): node index

    Returns:
        bool: True on success, else False

        Node of node type at index removed from database instance
    '''

    # remove node from database instance by node type and index
    del _db[_type][_index]

    # on success, return True
    return True



def add_relation(_db, _node_type, _node_index, _rels_type, _rels_index):

    ''' Add Node Relation

        Add node to node relation by node types and indicies

    Args:
        _db (dict): database instance
        _node_type (str): type of node to add relation to
        _node_index (str): index of node to add relation to within database node type list
        _rels_type (str): type of node relation being added
        _rels_index (str): index of node relation

    Returns:
        bool: True on success, else False
    '''

    # get node relations
    node_rels = _db[_node_type][_node_index]['rels']

    # check for relation list at node exists, else create
    if _rels_type not in node_rels.keys():
        node_rels[_rels_type] = []

    # add relation to node
    node_rels[_rels_type].append(_rels_index)

    # return True upon success
    return True
