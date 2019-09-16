
''' Jupyter Notebook Wrapper Functions

Summary:
    This file wrapper and helper functions for operating pvlibs data processing and analysis jupyter notebooks

Example:
    Usage of

Todo:
    *
'''



''' Imports '''

# database module
#from . import database

# data import module
from . import data_import

# data processing module
from . import process_data

# general functions module
from . import general


# filesystem navigation, system, regex
import glob

# pandas dataframe
import pandas as pd

import numpy as np

# matplotlib plotting library
import matplotlib.pyplot as plt

# python image library
import PIL

from scipy import ndimage



''' Helper Functions '''

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

        # print file name
        print('imported reference to file: {}'.format(file_name))



def select_node(db, node_filter):

    ''' Select Node in Database

    Args:
        db (list): database instance as list of file nodes (dict)
        node_filter (dict): dict of node parameters to search / filter by

    Returns:
        (dict): first node match within database instance
    '''

    # iterate each node in database
    for i in range(len(db)):
        node = db[i]


        # get number parameter matches within node
        match = sum([ 1 for key, value in node_filter.items() if key in node.keys() and node[key] == value ])

        # if every parameter has been successfully matched
        if match == len(node_filter.keys()):

            # return first matched node
            return node



''' Wrapper Functions '''

def init_file_db(base_path, props):

    ''' Initialise Measurement File Database

    Args:
        base_path (str): full directory path to search
        props (dict): file properties to store in each measurement file node

    Returns:
        (list): database instance populated with measurement file nodes
    '''

    # initialise blank database (list)
    db = []


    print('begin file search and import \n')

    # search for data files and store in database
    add_files(db, base_path, props)

    print('\nfile search and import complete')

    print('\n{} measurement file references imported'.format(len(db)))


    # return populated database
    return db



def parse_file_names(db, param_sep, params):

    ''' Parse Node File Name Parameters

    Args:
        db (list): database instance as list of file nodes (dict)
        param_sep (str): file name parameter separator character
        params (list): ordered list of parameters to parse from file node file name

    Returns:
        (none): file name parameters added to each node in database instance
    '''

    # build parse string from ordered parameter list and separator
    #match_str = '[^{}]'.format(param_sep)
    match_str = '.+'
    parse_string = '^{}\..+$'.format( param_sep.join( [ '(?P<{}>{})'.format(p, match_str) for p in params ] ) )


    print('begin file name parameter parsing \n')


    # iterate each node in database
    for i in range(len(db)):
        node = db[i]

        print('parsing: file {}/{}'.format(i+1, len(db)))


        # parse node file name using parse string as regular expression
        filename_params = general.str_parse_params(_string = node['file_name'], _parse_string = parse_string)

        # if successful regex match
        if filename_params is not None:

            # store each file name parameter in measurement node
            for key, value in filename_params.items():
                node[key] = value


        # if file anme parse failed
        else:
            print('parsing parameters failed for file: {}'.format( node['file_name'] ))


    print('\nfile name parameter parsing complete')


    # discard any nodes where failed to parse parameters by filter on first parameter
    db = [ d for d in db if params[0] in d.keys() ]

    print('\n{} file names parsed'.format(len(db)))

    return db



def import_file_data(db):

    ''' Import Data from File

    Args:
        db (list): database instance as list of file nodes (dict)

    Returns:
        (none): imported data added to each node in database instance
    '''

    print('begin file data import \n')

    # iterate each node in database
    for i in range(len(db)):
        node = db[i]

        print('importing: file {}/{}'.format(i+1, len(db)))

        try:

            # import data from file by node parameters
            data = data_import.core.import_data_file(
                meas_type = node['meas_type'],
                file_type = node['file_type'],
                file_path = node['file_path'],
                file_name = node['file_name'],
            )

            # store all imported data in measurement node
            for key, value in data.items():
                node[key] = value


        # on data import error
        except:
            print('failed to import data from file: {}'.format(node['file_name']))


    print('\ndata file import complete')


    # discard any nodes where failed to parse parameters by filter on first data entry
    db = [ d for d in db if list(data.keys())[0] in d.keys() ]

    print('\ndata imported from {} files'.format(len(db)))

    return db


def process_file_data(db, meas_type = None, params = {}):

    ''' Import Data from File

    Args:
        db (list): database instance as list of file nodes (dict)
        meas_type (str): measurement type for processing
        params (dict): additional parameters for processing

    Returns:
        (none): imported data added to each node in database instance
    '''

    print('begin measurement data processing \n')

    # iterate each node in database
    for i in range(len(db)):
        node = db[i]

        print('processing: measurement {}/{}'.format(i+1, len(db)))

        try:

            # update node with additional parameters
            for key, value in params.items():
                node[key] = value

            # use existing default measurement type for process if not provided
            if meas_type is None:
                meas_type = node['meas_type']

            # import data from file by node parameters
            data = process_data.core.process_data(
                meas_type = meas_type,
                data = node,
            )

            # store all imported data in measurement node
            for key, value in data.items():
                node[key] = value


        # on data import error
        except:
            print('failed to process measurement: {}'.format(node['file_name']))


    print('\nmeasurement data processing complete')


    # discard any nodes where failed to parse parameters by filter on first data entry
    db = [ d for d in db if list(data.keys())[0] in d.keys() ]

    print('\n{} measurements processed'.format(len(db)))

    return db


def plot_mlt_fit(db, params):

    ''' Plot Sinton Lifetime Model Fit

    Args:
        db (list): database instance as list of file nodes (dict)
        params (dict): node containing sinton lifetime model fit data

    Returns:
        (none): figure displayed
    '''

    # get selected node by first parameter match in database
    _node = select_node(db, params)

    ## need to ensure found a node, else fail gracefully


    # print selected model fit parameters
    print('Implied Open Circuit Voltage (iVoc) = {:.1f} [mV]'.format(_node['ivoc']*1e3))
    print('Surface Recombination Velocity (J_0) = {:.1f} [fa]'.format(_node['J_0']*1e15))
    print('Effective Lifetime = {:.1f} [us]'.format(_node['t_eff']*1e6))
    print('Bulk Lifetime = {:.1f} [us]'.format(_node['t_blk']*1e6))
    print('SRH K-value = {:.2f} []'.format(_node['k_val']))
    print('Model Fit Quality = {:.2f} [R^2]'.format(_node['R2']))


    # initialise figure and axes
    _w = 9; _h = 6
    fig = plt.figure(figsize = (_w, _h))
    fig.canvas.layout.width = '{}in'.format(_w)
    fig.canvas.layout.height= '{}in'.format(_h)

    ax = fig.add_subplot(111)


    # format figure axes
    #ax.set_xlim(5e13, 5e16)
    #ax.set_ylim(5e1, 5e6)

    ax.set_xscale('log')
    ax.set_yscale('log')

    ax.set_xlabel(r'Charge Density (cm$^{-3}$)')
    ax.set_ylabel(r'Inverse Carrier Lifetime (s)')


    # plot measured charge density dependent effective lifetime
    ax.plot(_node['nd'][::2], _node['tau'][::2]**-1, 'ok', label = 'measured', alpha = 0.3)


    # iterate and plot each model component
    for name, tau in _node.items():
        if name[:4] == 'tau_':

            # plot charge density dependent recombination lifetime component
            ax.plot(_node['dn'], tau**-1 , '--', label = '{}'.format(name), linewidth = 2, alpha = 0.6)


    # build and set figure title from params
    ax.set_title(' - '.join( [ '{}: {}'.format(k, v) for k, v in params.items() ] ))


    # display figure
    plt.legend(loc = 'upper left')
    plt.tight_layout()

    #plt.savefig('./results/lt-fit-B-control.png', dpi = 150)

    plt.show()



def save_mlt_fit(db, file_name_head, params):

    ''' Plot and Save Sinton Lifetime Model Fits

    Args:
        db (list): database instance as list of file nodes (dict)
        file_name_head (str): header inc path for output file name
        params (list): ordered list of parameters to use in plot output file name

    Returns:
        (none): figure saved to disk
    '''

    # iterate all nodes in database
    for _node in db:

        # initialise figure and axes
        _w = 9; _h = 6
        fig = plt.figure(figsize = (_w, _h))
        fig.canvas.layout.width = '{}in'.format(_w)
        fig.canvas.layout.height= '{}in'.format(_h)

        ax = fig.add_subplot(111)


        # format figure axes
        #ax.set_xlim(5e13, 5e16)
        #ax.set_ylim(5e1, 5e6)

        ax.set_xscale('log')
        ax.set_yscale('log')

        ax.set_xlabel(r'Charge Density (cm$^{-3}$)')
        ax.set_ylabel(r'Inverse Carrier Lifetime (s)')


        # plot measured charge density dependent effective lifetime
        ax.plot(_node['nd'][::2], _node['tau'][::2]**-1, 'ok', label = 'measured', alpha = 0.3)


        # iterate and plot each model component
        for name, tau in _node.items():
            if name[:4] == 'tau_':

                # plot charge density dependent recombination lifetime component
                ax.plot(_node['dn'], tau**-1 , '--', label = '{}'.format(name), linewidth = 2, alpha = 0.6)


        # build and set figure title from params
        ax.set_title(' - '.join( [ '{}: {}'.format(p, _node[p]) for p in params ] ))


        # display figure
        plt.legend(loc = 'upper left')
        plt.tight_layout()

        # build plot output file name from params
        file_name = '{}-{}.png'.format(file_name_head, '-'.join([ _node[p] for p in params ]))

        # save plot to file
        plt.savefig(file_name, dpi = 150)

        # close current figure
        plt.close()

        print('plot saved to file: {}'.format(file_name))



def compile_data(db, labels, values, file_name = 'results-summary'):

    ''' Compile Data and Export

    Args:
        db (list): database instance as list of file nodes (dict)
        labels (dict): dict of data labels as param key: output label value
        values (dict): dict of data values as param key: output label value

    Returns:
        (pd.DataFrame): pandas dataframe of compiled data
    '''

    # build data structure for compile dataset by labels and values
    data = {**{ v:[] for k,v in labels.items() }, **{ v:[] for k,v in values.items() } }


    # iterate each node in database
    for node in db:

        # store labels
        for k,v in labels.items():
            data[v].append( node[k] )

        # store values
        for k,v in values.items():
            data[v].append( node[k] )


    # store values in pandas dataframe
    data = pd.DataFrame(data)

    # print compiled dataset
    print(data.groupby(list(labels.values())).mean())


    # save summary data to file
    data.to_csv('./{}.csv'.format(file_name), index = False)


    print('\n complete "{}.csv" saved in current directory'.format(file_name))


    #return compiled data
    return data



def save_all_data(db, file_name_head, params, outputs = None):

    ''' Compile All Source and Calc Data and Export

    Args:
        db (list): database instance as list of file nodes (dict)
        file_name_head (str): header inc path for output file name
        params (list): ordered list of parameters to use in plot output file name

    Returns:
        (none): each measurement compiled data saved to file
    '''

    if outputs is None:

        # define data for output as dict of file: data params [list]
        outputs = {
            'raw': {
                'time': 'Measurement Time [s]',
                'conductance': 'Photo-conductance [V]',
                'illumination': 'Photon Density [cm^-3]',
            },
            'proc': {
                'nd': 'Charge Density [cm^-3]',
                'tau': 'Lifetime [s^-1]',
                'isuns': 'Implied Suns [suns]',
                'n_i_eff': 'Intrinsic Carrier Conc. [cm^-3]',
            },
            'fit': {
                'dn': 'Charge Density [cm^-3]',
                'tau_rad': 'Radiative Recombination Lifetime [s^-1]',
                'tau_aug': 'Auger Recombination Lifetime [s^-1]',
                'tau_sdr': 'Surface Defect Recombination Lifetime [s^-1]',
                'tau_srh': 'Bulk (SRH) Recombination Lifetime [s^-1]',
                'tau_eff': 'Effective Recombination Lifetime [s^-1]',
            },
        }

    # iterate each node in database
    for node in db:

        # iterate over output files
        for out, outs in outputs.items():

            # iterate over each data in output, store as dataset
            data = { v: node[k] for k,v in outs.items() }

            # store values in pandas dataframe
            data = pd.DataFrame(data)


            # build plot output file name from params
            file_name = '{}-{}-{}.csv'.format(file_name_head, out, '-'.join([ node[p] for p in params ]))

            # save summary data to file
            data.to_csv(file_name, index = False)

            print('data saved to file: {}'.format(file_name))




''' pl image processing '''

def norm_pl_exposure(db, ref_exp = None):

    ''' Normalise PL Images

    Args:
        db (list): database instance as list of file nodes (dict)
        ref_exp (float): reference exposure for normalisation

    Returns:
        (none): imported data added to each node in database instance
    '''

    print('begin pl image normalisation \n')


    # if not passed reference exposure value, find max
    if ref_exp is None:
        ref_exp = max([n['exposure'] for n in db])

    # iterate each node in database
    for i in range(len(db)):
        node = db[i]

        print('processing: measurement {}/{}'.format(i+1, len(db)))

        try:

            # update node with additional parameters
            node['norm_exposure'] = ref_exp


            # normalise pl images by exposure
            node['norm_img'] = ((node['raw_img'].astype(np.float64)  * ref_exp / node['exposure']))


        # on data import error
        except:
            print('failed to process measurement: {}'.format(node['file_name']))


    print('\nnormalisation complete')


    # discard any nodes where failed to parse parameters by filter on first data entry
    db = [ d for d in db if 'norm_img' in d.keys() ]

    print('\n{} measurements processed'.format(len(db)))

    return db



def save_norm_pl(db, file_name_head, params):

    ''' Save Normalised PL Images

    Args:
        db (list): database instance as list of file nodes (dict)
        file_name_head (str): header inc path for output file name
        params (list): ordered list of parameters to use in output file name

    Returns:
        (none): images saved to disk
    '''

    # iterate all nodes in database
    for node in db:

        # build output file name from params
        file_name = '{}-{}.tif'.format(file_name_head, '-'.join([ node[p] for p in params ]))


        # convert normalised image array to tif image
        img = PIL.Image.fromarray(node['norm_img'].astype(np.uint16))

        # save tif image to file
        img.save(file_name)


        print('image saved to file: {}'.format(file_name))




def fix_pl(db, params):

    ''' Fix PL Images

    Args:
        db (list): database instance as list of file nodes (dict)
        params (list): config parameters to use in image adjustment

    Returns:
        (none): figure saved to disk
    '''

    print('begin pl image adjustment \n')

    # iterate each node in database
    for i in range(len(db)):
        node = db[i]

        print('processing: measurement {}/{}'.format(i+1, len(db)))

        try:

            # get normalised image data
            img = node['norm_img']

            # rotate (align) and zero (top left) images, crop to wafer area (remove background)
            img = process_data.photoluminescence_image.rotate_zero_image(img,
                _angle_lim = params['angle_lim'],
                _angle_step = params['angle_step'],
                _edge = params['edge'],
            )

            # store trimmed image
            node['trim_img'] = img


        # on data import error
        except:
            print('failed to process measurement: {}'.format(node['file_name']))


    print('\nadjustments complete')


    # discard any nodes where failed to parse parameters by filter on first data entry
    db = [ d for d in db if 'trim_img' in d.keys() ]

    print('\n{} measurements processed'.format(len(db)))

    return db



def plot_ocpl(db, params):

    ''' Plot Sinton Lifetime Model Fit

    Args:
        db (list): database instance as list of file nodes (dict)
        params (dict): node containing sinton lifetime model fit data

    Returns:
        (none): figure displayed
    '''

    # get selected node by first parameter match in database
    _node = select_node(db, params)

    ## need to ensure found a node, else fail gracefully


    # diplay images
    _w = 9; _h = 5; fig = plt.figure(figsize = (_w, _h))
    fig.canvas.layout.width = '{}in'.format(_w); fig.canvas.layout.height= '{}in'.format(_h)
    #plt.xticks([]); plt.yticks([])
    ax = []; ax.append(fig.add_subplot(121)); ax.append(fig.add_subplot(122))


    ax[0].imshow(_node['raw_img'], cmap = 'magma')
    ax[0].set_xticks([]); ax[0].set_yticks([])

    ax[1].imshow(_node['trim_img'], cmap = 'magma')
    ax[1].set_xticks([]); ax[1].set_yticks([])


    plt.tight_layout()

    plt.show()





def pl_hist_stats(db, params):

    ''' Fix PL Images

    Args:
        db (list): database instance as list of file nodes (dict)
        params (list): config parameters to use in image adjustment

    Returns:
        (none): figure saved to disk
    '''

    print('begin stats calc \n')

    # iterate each node in database
    for i in range(len(db)):
        node = db[i]

        print('processing: measurement {}/{}'.format(i+1, len(db)))

        try:

            # get normalised image data
            img = node['norm_img']


            if 'floor' in params.keys():
                j = np.where(img >= params['floor'])
                img = img[j]


            # set histogram parameters
            _min = 0.1
            _max = np.max(img)

            bins = params['bins']

            # make histogram bins
            x = np.linspace(_min, _max, bins)

            # calculate histogram of image data (photoluminescence counts)
            hist = ndimage.measurements.histogram(img, _min, _max, bins)

            # calculate area normalised histogram (fraction pixels)
            #hist_frac = hist / ( (img.shape[0] * img.shape[1]) )
            hist_frac = hist / img.shape[0]


            # store histogram data
            node['hist_bins'] = x
            node['hist_cnts'] = hist
            node['hist_norm'] = hist_frac


            # calculate and store statistics
            node['med'] = np.median(img)
            node['avg'] = np.mean(img)
            node['std'] = np.std(img)


        # on data import error
        except:
            print('failed to process measurement: {}'.format(node['file_name']))


    print('\nstats calc complete')


    # discard any nodes where failed to parse parameters by filter on first data entry
    db = [ d for d in db if 'norm_img' in d.keys() ]

    print('\n{} measurements processed'.format(len(db)))

    return db





def save_pl_hist(db, file_name_head, params):

    ''' Plot and Save PL Histograms

    Args:
        db (list): database instance as list of file nodes (dict)
        file_name_head (str): header inc path for output file name
        params (list): ordered list of parameters to use in plot output file name

    Returns:
        (none): figure saved to disk
    '''

    # iterate all nodes in database
    for node in db:

        # diplay images
        _w = 7; _h = 5; fig = plt.figure(figsize = (_w, _h))
        fig.canvas.layout.width = '{}in'.format(_w); fig.canvas.layout.height= '{}in'.format(_h)
        #plt.xticks([]); plt.yticks([])

        plt.xlabel('Photoluminescence Intensity (Cnts.)')
        plt.ylabel('Area Fraction')


        x = node['hist_bins']
        hist = node['hist_norm']
        #hist = node['hist_cnts']

        # stem plot histogram
        st = plt.stem(x, hist, linefmt = '-', markerfmt = '-', basefmt = 'k-', use_line_collection = True)

        m = node['med']
        plt.vlines(m, 0., np.max(hist)*1.1, colors = 'r')

        s = node['std']
        plt.vlines([m-s, m+s], 0., np.max(hist)*1.1, colors = 'k', linestyles = '--', alpha = 0.5)


        # display figure
        plt.tight_layout()

        # build plot output file name from params
        file_name = '{}-{}.png'.format(file_name_head, '-'.join([ node[p] for p in params ]))

        plt.savefig(file_name)

        plt.close()


        print('plot saved to file: {}'.format(file_name))
