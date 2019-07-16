
''' Database Search Functions

Summary:
    This file contains database search functions

Example:
    Usage of the search functions

        #

Todo:
    * return a database instance with subset filtered by: function of node types and parameters; obtain all nodes
    within search / filter query, primary node type (provided); select relations (node types) to keep (default all),
    rebuild relations within new subset database instance; return new database instance
'''



''' Database Search and Filter Functions '''

def get_index_match_params(_db, _type, _params):

    ''' Filter Dataset by Contains Parameter

        Given a list of parameters (key: value), match nodes within database list by type and return node indicies;
        greedy OR match to params: given list of key:value param pairs, node is a match if any pair match

    Args:
        _db (dict): database instance
        _type (str): database list type
        _params (dict): node parameters to match within database list

    Returns:
        list: matched indicies within database
    '''

    # build index list from data array, match all params per data entry
    indicies = []

    # get database list by type
    db_list = _db[_type]

    # iterate each node in database list
    for i in range(len(db_list)):
        node_params = db_list[i]['params']

        # iterate each parameter
        for key, value in _params.items():

            # check for parameter in node
            if key in node_params.keys():

                # check for match to parameter value
                if node_params[key] == value:

                    # add node index to incidies list
                    indicies.append(i)


    # return index list
    return indicies



def get_index_hard_match_params(_db, _type, _params):

    ''' Filter Dataset by Contains Parameter

        Given a list of parameters (key: value), match nodes within database list by type and return node indicies;
        greedy OR match to params: given list of key:value param pairs, node is a match if any pair match

    Args:
        _db (dict): database instance
        _type (str): database list type
        _params (dict): node parameters to match within database list

    Returns:
        list: matched indicies within database
    '''

    # build index list from data array, match all params per data entry
    indicies = []

    # get database list by type
    db_list = _db[_type]

    # iterate each node in database list
    for i in range(len(db_list)):
        node_params = db_list[i]['params']


        # get number parameter matches within node
        match = sum([ 1 for key, value in _params.items() if key in node_params.keys() and node_params[key] == value ])

        # if every parameter has been successfully matched
        if match == len(_params.keys()):

            # add node index to incidies list
            indicies.append(i)


    # return index list
    return indicies




def get_index_rels(_db, _type, _params, _rel_type):

    ''' Get Relation Indicies by Type

        Search database list by type and match params to obtain node indicies; compile list of node relations for each
        matched node by relation type; returns a list of matched nodes, each with index and a list of relation indicies

    Args:
        _db (dict): database instance
        _type (str): database list type (node with relations)
        _params (dict): node parameters to match within database list
        _rel_type (str): node relation type to obtain indicies list


    Returns:
        list: list for each mtched node, relation indicies within node by type
    '''

    # get indicies of node type what match params
    indicies = get_index_match_params(_db = _db, _type = _type, _params = _params)

    # initialise list of relation lists per node match
    relations = []

    # iterate over matches
    for index in indicies:

        # get relations by type within node, store
        rels = _db[_type][index]['rels'][_rel_type]

        # store relations indicies in dict with index in type database list
        relations.append( {'index': index, 'rels': rels} )


    # return list of relation dicts
    return relations
