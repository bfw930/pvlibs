
''' Core Orchestration Protocols

Summary:
    This file contains

Example:
    Usage of

Todo:
    *
'''



''' Imports '''

import os, shutil

from ipyupload import FileUpload



''' File Upload Handling '''

def file_upload_widget(accept = ['.xlsm', '.ltr']):

    ''' Generate File Upload Widget

        build and return file upload jupyter notebook widget

    Args:

    Returns:
        (obj): file upload widget instance
    '''

    # define file upload widget
    w = FileUpload(
        #accept = '.csv',
        accept = ', '.join(accept),
        multiple = True,
        disabled = False,
        style_button = '',
        compress_level = 0, # 0-9
    )

    # return file upload widget
    return w



def file_upload(w):

    ''' Generate File Upload Widget

        build and return file upload jupyter notebook widget

    Args:
        w (ipyupload ref): widget reference with uploaded files

    Returns:
        (obj): files stored to disc
    '''

    # check for upload directory, create if does not exist, clean if does exist
    if 'upload' not in os.listdir('./'):
        os.makedirs('./upload')
    else:
        shutil.rmtree('./upload', ignore_errors=True)
        os.makedirs('./upload')

    # iterate all files uploaded through widget
    for file_name, content in w.value.items():

        # write binary file data uploaded through widget to file
        with open('./upload/{}'.format(file_name), 'wb') as file:
            file.write( content['content'] )

        # print file name after successful upload
        print('{} uploaded'.format(file_name))



def clear_uploads():

    ''' Generate File Upload Widget

        build and return file upload jupyter notebook widget

    Args:
        w (ipyupload ref): widget reference with uploaded files

    Returns:
        (obj): files stored to disc
    '''

    # check for upload directory, clean if exists
    if 'upload' in os.listdir('./'):
        shutil.rmtree('./upload', ignore_errors=True)
        print('uploads removed')

    else:
        print('no uploads found')
