
''' Core Orchestration Protocols

Summary:
    This file contains

Example:
    Usage of

Todo:
    *
'''



''' Imports '''

# data array handling
import numpy as np


from scipy.stats import linregress
from scipy.signal import savgol_filter

# image convolution and analysis
import scipy.ndimage as ndimage

from scipy.signal import correlate

# database search functions
from .. import database



''' Core Calculation Functions '''






''' Data Processing Functions '''

def process_photoluminescence_image(_db, ):

    ''' Process

        Process

    Args:
        _db (dict): database instance
        _device_id (str): device id to process

    Returns:
        dict: calculated derivative data
    '''

    # get device node index by device id
    device_index = database.get_index_match_params(_db, 'device', {'device_id': _device_id})[0]

    # get device parameters
    device_params = _db['device'][device_index]['params']


    # get device measurement indicies
    measurement_indicies = _db['device'][device_index]['rels']['measurement']

    # get current-voltage data for 1 sun illumination
    full_data = [ m for m in [ _db['measurement'][i] for i in measurement_indicies ]
        if m['params']['measurement_subtype'] == 'full' ][0]['data']


    # calculate device solar performance from 1 sun current-voltage data
    performance_data = calc_performance(_data = full_data, _params = device_params)


    # return calculated results
    return {'solar_performance': performance_data}




def rotate_zero_image(_img, _angle_lim = 1.5, _angle_step = 0.1, _edge = .1):


    #pad_img = np.pad(_img, ((20,20),(20,20)), 'constant')

    top = []; bottom = []; left = []; right = []
    angles = np.arange(-_angle_lim, _angle_lim, _angle_step)
    for i in range(len(angles)):

        #img = _img/_img.max()

        img = ndimage.interpolation.rotate(_img, angles[i], reshape = False, mode = 'nearest')
        img = ndimage.morphological_laplace(img, 5)

        h_line = np.mean(img, axis = 1)
        v_line = np.mean(img, axis = 0)

        h_line = savgol_filter(x = h_line, window_length = 15, polyorder = 2, mode = 'mirror', deriv = 0)
        v_line = savgol_filter(x = v_line, window_length = 15, polyorder = 2, mode = 'mirror', deriv = 0)

        j = np.where( h_line == h_line[:int(h_line.shape[0]*_edge)].min() )[0][0]
        top.append( [ h_line[ j ], j, angles[i] ] )

        j = np.where( h_line == h_line[-int(h_line.shape[0]*_edge):].min() )[0][0]
        bottom.append( [ h_line[ j ], j, angles[i] ] )

        j = np.where( v_line == v_line[:int(v_line.shape[0]*_edge)].min() )[0][0]
        left.append( [ v_line[ j ], j, angles[i] ] )

        j = np.where( v_line == v_line[-int(v_line.shape[0]*_edge):].min() )[0][0]
        right.append( [ v_line[ j ], j, angles[i] ] )

    top = np.stack(top, axis = 0)
    bottom = np.stack(bottom, axis = 0)
    left = np.stack(left, axis = 0)
    right = np.stack(right, axis = 0)


    # get average of edges
    avg = []
    sets = [top, bottom, left, right]
    for i in range(len(sets)):
        _set = sets[i][np.argsort(sets[i][:,2]),:]
        avg.append(_set[:, 0])
    avg = np.median( np.vstack(avg).T, axis = 1)


    sy = savgol_filter(x = avg, window_length = 15, polyorder = 2, mode = 'mirror', deriv = 0)
    j = np.where(sy == sy.min())[0]
    angle = sets[0][j, 2][0]
    edges = [ s[j, 1] for s in sets ]


    # rotate image by reverse angle
    img = ndimage.interpolation.rotate(_img, angle, reshape = False, mode = 'nearest')

    # crop image to edges
    img = img[ int(edges[0]):int(edges[1]), int(edges[2]):int(edges[3]) ]


    return img



def get_angle_edges(_img, _angle_lim = 1.5, _angle_step = 0.1, _edge = .1):


    #pad_img = np.pad(_img, ((20,20),(20,20)), 'constant')

    top = []; bottom = []; left = []; right = []
    angles = np.arange(-_angle_lim, _angle_lim, _angle_step)
    for i in range(len(angles)):

        #img = _img/_img.max()

        img = ndimage.interpolation.rotate(_img, angles[i], reshape = False, mode = 'nearest')
        img = ndimage.morphological_laplace(img, 5)

        h_line = np.mean(img, axis = 1)
        v_line = np.mean(img, axis = 0)

        h_line = savgol_filter(x = h_line, window_length = 15, polyorder = 2, mode = 'mirror', deriv = 0)
        v_line = savgol_filter(x = v_line, window_length = 15, polyorder = 2, mode = 'mirror', deriv = 0)

        j = np.where( h_line == h_line[:int(h_line.shape[0]*_edge)].min() )[0][0]
        top.append( [ h_line[ j ], j, angles[i] ] )

        j = np.where( h_line == h_line[-int(h_line.shape[0]*_edge):].min() )[0][0]
        bottom.append( [ h_line[ j ], j, angles[i] ] )

        j = np.where( v_line == v_line[:int(v_line.shape[0]*_edge)].min() )[0][0]
        left.append( [ v_line[ j ], j, angles[i] ] )

        j = np.where( v_line == v_line[-int(v_line.shape[0]*_edge):].min() )[0][0]
        right.append( [ v_line[ j ], j, angles[i] ] )

    top = np.stack(top, axis = 0)
    bottom = np.stack(bottom, axis = 0)
    left = np.stack(left, axis = 0)
    right = np.stack(right, axis = 0)


    # get average of edges
    avg = []
    sets = [top, bottom, left, right]
    for i in range(len(sets)):
        _set = sets[i][np.argsort(sets[i][:,2]),:]
        avg.append(_set[:, 0])
    avg = np.median( np.vstack(avg).T, axis = 1)


    sy = savgol_filter(x = avg, window_length = 15, polyorder = 2, mode = 'mirror', deriv = 0)
    j = np.where(sy == sy.min())[0]
    angle = sets[0][j, 2][0]
    edges = [ s[j, 1] for s in sets ]


    # rotate image by reverse angle
    #img = ndimage.interpolation.rotate(_img, angle, reshape = False, mode = 'nearest')

    # crop image to edges
    #img = img[ int(edges[0]):int(edges[1]), int(edges[2]):int(edges[3]) ]


    #return img
    return angle, edges



def rotate_zero_shift_image(_img, _angle_lim = 1.5, _angle_step = 0.1, _edge = .1):

    top = []; bottom = []; left = []; right = []
    angles = np.arange(-_angle_lim, _angle_lim, _angle_step)
    for i in range(len(angles)):

        img = ndimage.interpolation.rotate(_img, angles[i], reshape = False, mode = 'nearest')
        img = ndimage.morphological_laplace(img, 5)

        h_line = np.mean(img, axis = 1)
        v_line = np.mean(img, axis = 0)

        h_line = savgol_filter(x = h_line, window_length = 15, polyorder = 2, mode = 'mirror', deriv = 0)
        v_line = savgol_filter(x = v_line, window_length = 15, polyorder = 2, mode = 'mirror', deriv = 0)

        j = np.where( h_line == h_line[:int(h_line.shape[0]*_edge)].min() )[0][0]
        top.append( [ h_line[ j ], j, angles[i] ] )

        j = np.where( h_line == h_line[-int(h_line.shape[0]*_edge):].min() )[0][0]
        bottom.append( [ h_line[ j ], j, angles[i] ] )

        j = np.where( v_line == v_line[:int(v_line.shape[0]*_edge)].min() )[0][0]
        left.append( [ v_line[ j ], j, angles[i] ] )

        j = np.where( v_line == v_line[-int(v_line.shape[0]*_edge):].min() )[0][0]
        right.append( [ v_line[ j ], j, angles[i] ] )

    top = np.stack(top, axis = 0)
    bottom = np.stack(bottom, axis = 0)
    left = np.stack(left, axis = 0)
    right = np.stack(right, axis = 0)


    # get average of edges
    avg = []
    sets = [top, bottom, left, right]
    for i in range(len(sets)):
        _set = sets[i][np.argsort(sets[i][:,2]),:]
        avg.append(_set[:, 0])
    avg = np.median( np.vstack(avg).T, axis = 1)


    sy = savgol_filter(x = avg, window_length = 15, polyorder = 2, mode = 'mirror', deriv = 0)
    j = np.where(sy == sy.min())[0]
    angle = sets[0][j, 2][0]
    edges = [ s[j, 1] for s in sets ]


    # rotate image by reverse angle
    img = ndimage.interpolation.rotate(_img, angle, reshape = False, mode = 'nearest')

    # shift image to top-left zero
    img = ndimage.interpolation.shift(_img, shift = [-int(edges[0]), -int(edges[2])], mode = 'nearest')

    # crop image to edges
    #img = img[ int(edges[0]):int(edges[1]), int(edges[2]):int(edges[3]) ]


    return img



def get_diff_image(_img, _ref):

    _pre = _ref
    _post = _img

    # image max shape for padding
    _shape = ( np.max([_pre.shape[0], _post.shape[0]]), np.max([_pre.shape[1], _post.shape[1]]))
    _pre = np.pad(_pre, ((0,_shape[0] - _pre.shape[0]),(0,_shape[1] - _pre.shape[1])), 'constant' )
    _post = np.pad(_post, ((0,_shape[0] - _post.shape[0]),(0,_shape[1] - _post.shape[1])), 'constant' )

    # get difference and apply median filter
    _diff = (_post - _pre) / _post
    #_diff = _post - _pre

    j = np.where(_diff < 0)
    _diff[j] = 0
    j = np.where( np.isnan(_diff) )
    _diff[j] = 0

    _diff = ndimage.median_filter(_diff, size = 5)


    return _pre, _post, _diff


def align_images(_img, _ref, _mode = 'rough'):


    if _mode == 'fine':
        scale = .5
        angles = np.arange(-.2, .2, .01)
    elif _mode == 'alright':
        scale = .6
        angles = np.arange(-.1, .1, .01)
    else:
        scale = .2
        angles = np.arange(-1.2, 1.2, .1)

    # scale images
    img = ndimage.zoom(_img, scale)
    ref = ndimage.zoom(_ref, scale)

    # noramlise PL count
    img = img / img.max()
    ref = ref / ref.max()

    # increase dimensionality of image
    _imgs = np.stack([img], axis = 2)

    _refs = []

    # iterate range of relative rotate angles
    for i in range(len(angles)):

        # stack rotated images into additional dimension
        _refs.append( ndimage.interpolation.rotate(ref, angles[i], reshape = False, mode = 'constant') )
    _refs = np.stack(_refs, axis = 2)


    # perform correlation between image and reference (inc. rotations)
    cor = correlate(_imgs, _refs, mode = 'full')

    # at maximum correlation, extract angle and x,y shifts
    j = np.where(cor == cor.max())
    angle = -angles[j[2][0]]
    shift_x = ((j[0][0] - cor.shape[0]/2)/cor.shape[0])*_img.shape[0]*2
    shift_y = ((j[1][0] - cor.shape[1]/2)/cor.shape[1])*_img.shape[0]*2

    print(angle, shift_x, shift_y)


    # adjust reference image
    img = ndimage.interpolation.rotate(_ref, angle, reshape = False, mode = 'constant')
    img = ndimage.shift(img, (shift_x, shift_y), mode = 'constant')


    # return aligned reference image
    return img
