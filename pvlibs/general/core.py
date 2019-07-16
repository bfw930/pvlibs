
''' General Functions

Summary:
    This file contains

Example:
    Usage of

Todo:
    *
'''



''' Imports '''

# filesystem parsing, regex handling
import re



''' General Helper Functions '''

def str_parse_params(_string, _parse_string):

    ''' Extract Params from String

        Given a string (eg filename) and regex format string, return dict of each parameter and value

    Args:
        _string (str): string to parse and extract parameters from
        _parse_string (str): name parse format (regex with groups for params)

    Returns:
        dict: extracted paramaters parsed from name
    '''

    # extract list of parameters in parse string
    params = re.findall('<([^<>]*)>', _parse_string)

    # parse name
    re_name = re.search(_parse_string, _string)

    # check for valid parse string
    if re_name is not None:

        # iterate and extract each parameter
        values = [ re_name.group(param) for param in params ]

        # return named dict of extracted parameter values
        params = { params[i]:values[i] for i in range(len(params)) }
        return params

    # if name parse error
    else:
        # warn of parse error, entry discarded
        #print( 'invalid string: ' + _string )
        pass
