
''' Imports '''

# parse functions specific to sinton lifetime measurements
from .sinton_lifetime import parse_sinton_lifetime

# parse functions specific to sinton suns-voc measurements
from .sinton_suns_voc import parse_sinton_suns_voc

# parse functions specific to current-voltage measurements
from .current_voltage import parse_current_voltage

# parse functions specific to quantum_efficiency measurements
from .quantum_efficiency import parse_quantum_efficiency

# parse functions specific to photoluminescence_image measurements
from .photoluminescence_image import parse_photoluminescence_image

# ecv import
from .ecv import parse_ecv

# sheet res import
from .sheet_res import parse_sheet_res



# open-circuit photoluminescence
from .ocpl import ocpl

# sinton lifetime
from .slt import slt

# current-voltage
from .iv import iv

# loana datasets
from .loana import loana



''' Core Data Import Functions '''

def parse_data_file(_file_path, _format):

    ''' Parse File

        Parse source data file of given measurement and format

    Args:
        _file_path (str): full file path including name with extension
        _measurement (str): measurement type for generated data file
        _format (dict): data file format information

    Returns:
        dict: data parsed from file
    '''

    # sinton lifetime measurement
    if _format['measurement'] == 'sinton_lifetime':

        # parse and process source data file, return imported data
        return parse_sinton_lifetime(_file_path, _format)


    # sinton suns-voc measurement
    if _format['measurement'] == 'sinton_suns_voc':

        # parse and process source data file, return imported data
        return parse_sinton_suns_voc(_file_path, _format)


    # current-voltage measurement
    if _format['measurement'] == 'current_voltage':

        # parse and process source data file, return imported data
        return parse_current_voltage(_file_path, _format)


    # quantum_efficiency measurement
    if _format['measurement'] == 'quantum_efficiency':

        # parse and process source data file, return imported data
        return parse_quantum_efficiency(_file_path, _format)


    # photoluminescence_image measurement
    if _format['measurement'] == 'photoluminescence_image':

        # parse and process source data file, return imported data
        return parse_photoluminescence_image(_file_path, _format)


    # ECV measurement
    if _format['measurement'] == 'ecv':

        # parse and process source data file, return imported data
        return parse_ecv(_file_path, _format)


    # sheet res measurement
    if _format['measurement'] == 'sheet_res':

        # parse and process source data file, return imported data
        return parse_sheet_res(_file_path, _format)



def import_data_file(meas_type, file_type, file_path, file_name):

    ''' Import Data from File

        Import source measurement data from file of given measurement and file type

    Args:
        meas_type (str): data file measurement type
        file_type (str): data file format type
        file_path (str): full path of data file
        file_name (str): data file name inc. ext.

    Returns:
        dict: data imported from file
    '''

    # open circuit photoluminescence measurement
    if meas_type == 'ocpl':

        # import data from file, return imported data
        data = ocpl(file_type = file_type, file_path = file_path, file_name = file_name)


    # sinton lifetime measurement
    if meas_type == 'slt':

        # import data from file, return imported data
        data = slt(file_type = file_type, file_path = file_path, file_name = file_name)


    # current-voltage measurement
    if meas_type == 'iv':

        # import data from file, return imported data
        data = iv(file_type = file_type, file_path = file_path, file_name = file_name)


    # loana measurement
    if meas_type == 'loana':

        # import data from file, return imported data
        data = loana(file_type = file_type, file_path = file_path, file_name = file_name)

    # wavelabs measurement
    if meas_type == 'wavelabs':

        # import data from file, return imported data
        data = iv(file_type = file_type, file_path = file_path, file_name = file_name)


    # return imported data
    return data
