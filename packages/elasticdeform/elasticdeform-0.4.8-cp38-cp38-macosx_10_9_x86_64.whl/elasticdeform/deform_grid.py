import numpy
import scipy.ndimage

from . import _deform_grid

def deform_random_grid(X, sigma=25, points=3, order=3, mode='constant', cval=0.0,
                       crop=None, prefilter=True, axis=None,
                       affine=None, rotate=None, zoom=None):
    """
    Elastic deformation with a random deformation grid

    This generates a random, square deformation grid with displacements
    sampled from from a normal distribution with standard deviation `sigma`.
    The deformation is then applied to the image or list of images,

    See ``deform_grid`` for a full description of the parameters.

    Parameters
    ----------
    X : numpy array or list of arrays
        image, or list of images of the same size
    sigma : float
        standard deviation of the normal distribution
    points : array
        number of points of the deformation grid
    rotate : float or None
        angle in degrees to rotate the output

        This only works for 2D images and rotates the image around
        the center of the output.
    zoom : float or None
        scale factor to zoom the output

        This only works for 2D images and scales the image around
        the center of the output.

    See Also
    --------
    deform_grid : for a full description of the parameters.
    """
    # prepare inputs and axis selection
    Xs = _normalize_inputs(X)
    axis, deform_shape = _normalize_axis_list(axis, Xs)

    if not isinstance(points, (list, tuple)):
        points = [points] * len(deform_shape)

    displacement = numpy.random.randn(len(deform_shape), *points) * sigma
    return deform_grid(X, displacement, order, mode, cval, crop, prefilter, axis, affine, rotate, zoom)


def deform_grid(X, displacement, order=3, mode='constant', cval=0.0, crop=None, prefilter=True, axis=None,
                affine=None, rotate=None, zoom=None):
    """
    Elastic deformation with a deformation grid

    The procedure generates a coarse displacement grid with a random displacement
    for each grid point. This grid is then interpolated to compute a displacement for
    each pixel in the input image. The input image is then deformed using the
    displacement vectors and a spline interpolation.

    Parameters
    ----------
    X : numpy array or list of arrays
        image, or list of images of the same size

        If X is a list of images, the values for order, mode and cval can be lists
        to specify a different value for every image in X.
    displacement : numpy array
        displacement vectors for each control point

        displacement is a NumPy array with displacement vectors for each
        control points. For example, to deform a 2D image with 3 x 5 control
        points, provide a displacement matrix of shape 2 x 3 x 5.
    order : {0, 1, 2, 3, 4}
        interpolation order
    mode : ({nearest, wrap, reflect, mirror, constant})
        border mode
    cval : float
        constant value to be used if mode == 'constant'
    crop : None or list
        None, or a list of slice() objects to crop the output

        crop can be a list of slice() objects to crop the output with.
        Only very simple slicing is supported: the slice start and stop values must
        be positive and should not be larger than the output. Note that this parameter
        is dependent of the axis parameter: if an axis list is given, crop must only
        contain slice() objects for the dimensions in axis.
    prefilter : bool
        if True the input X will be pre-filtered with a spline filter
    axis : None, int, a list of ints, or a list of lists of ints
        the axes to deform over

        axis indicates the axes on which the deformation should be applied.
        The default (None) is to apply a deformation to all dimensions of the input.
        Giving a single axis (int) or a tuple of axes will apply the deformation only
        to those axes. The shape of the displacement must match this number of axes.
        If multiple inputs are given, axis should be None or a list of tuples with
        the axes for each input.
    affine : None, numpy array of shape (ndim, ndim + 1)
        affine transformation to apply to the output

        The affine transformation is applied to the output during interpolation.
    rotate : float or None
        angle in degrees to rotate the output

        This only works for 2D images and rotates the image around
        the center of the output.
    zoom : float or None
        scale factor to zoom the output

        This only works for 2D images and scales the image around
        the center of the output.

    Returns
    -------
    numpy array or list of arrays
        The deformed image, or a list of deformed images if a list of inputs is given.

    Notes
    -----
    See the SciPy documentation for scipy.ndimage.interpolation.map_coordinates
    for more details on some of the parameters.

    The elastic deformation approach is found in

    * Ronneberger, Fischer, and Brox, "U-Net: Convolutional Networks for Biomedical
      Image Segmentation"  https://arxiv.org/abs/1505.04597
    * Cicek et al., "3D U-Net: Learning Dense Volumetric
      Segmentation from Sparse Annotation"  https://arxiv.org/abs/1606.06650

    Based on a Python implementation by Florian Calvet.
    """
    # prepare inputs and axis selection
    Xs = _normalize_inputs(X)
    axis, deform_shape = _normalize_axis_list(axis, Xs)

    # prepare output cropping
    output_shapes, output_offset = _compute_output_shapes(Xs, axis, deform_shape, crop)

    # prepare other parameters
    displacement = _normalize_displacement(displacement, Xs, axis)
    order = _normalize_order(order, Xs)
    mode = _normalize_mode(mode, Xs)
    cval = _normalize_cval(cval, Xs)
    affine = _normalize_affine(affine, axis)

    # compute inverse affine given output affine
    inverse_affine = _compute_inverse_affine(affine)

    # add rotation and zoom to the inverse affine matrix
    inverse_affine = _apply_rotation_and_zoom(rotate, zoom, inverse_affine, [output_shapes[0][d] for d in axis[0]])

    # prefilter inputs
    Xs_f = []
    for i, x in enumerate(Xs):
        if prefilter and order[i] > 1:
            x_f = numpy.zeros_like(x)
            for d in axis[i]:
                scipy.ndimage.spline_filter1d(x, axis=d, order=order[i], output=x_f)
                x = x_f
            Xs_f.append(x_f)
        else:
            Xs_f.append(x)
    # prefilter displacement
    displacement_f = numpy.zeros_like(displacement)
    for d in range(1, displacement.ndim):
        scipy.ndimage.spline_filter1d(displacement, axis=d, order=3, output=displacement_f)
        displacement = displacement_f

    # prepare output arrays
    outputs = [numpy.zeros(os, dtype=x.dtype) for os, x in zip(output_shapes, Xs)]

    _deform_grid.deform_grid(Xs_f, displacement_f, output_offset, outputs, axis, order, mode, cval, inverse_affine)

    if isinstance(X, list):
        return outputs
    else:
        return outputs[0]


def deform_grid_gradient(dY, displacement, order=3, mode='constant', cval=0.0, crop=None,
                         prefilter=True, axis=None, X_shape=None,
                         affine=None, rotate=None, zoom=None):
    """
    Gradient for deform_grid.

    This method performs the backward operation that returns the gradient of deform_grid
    with respect to the input. This is similar to performing an inverse deformation on
    the gradient, but not exactly the same: this function gives an exact gradient that
    also takes the interpolation into account.

    The X_shape parameter specifices the shape of the original inputs, and is only
    necessary if the crop parameter is used. Otherwise, the input shape is the same as
    the shape of the gradient dY.

    See the documentation for ``deform_grid``.

    Parameters
    ----------
    dY : numpy array
        the input gradient, or list of gradients of the same size
    displacement : numpy array
        displacement vectors for each control point
    order : {0, 1, 2, 3, 4}
        interpolation order
    mode : ({nearest, wrap, reflect, mirror, constant})
        border mode
    cval : float
        constant value to be used if mode == 'constant'
    crop : None or list
        None, or a list of slice() objects to crop the output
    prefilter : bool
        if True the input X will be pre-filtered with a spline filter
    axis : None, int, a list of ints, or a list of lists of ints
        the axes to deform over
    X_shape: tuple with the shape of the input, or a list of tuples
    affine : None, numpy array of shape (ndim, ndim + 1)
        affine transformation to apply to the output
    rotate : float or None
        angle in degrees to rotate the output
    zoom : float or None
        scale factor to zoom the output

    Returns
    -------
    numpy array
        Returns the gradient with respect to X.

    """
    # prepare inputs
    dYs = _normalize_inputs(dY)

    # find input shape
    if isinstance(X_shape, tuple):
        X_shape = [X_shape]
    elif X_shape is None:
        if crop is not None:
            raise ValueError("X_shape is required if the crop parameter is given.")
        X_shape = [dy.shape for dy in dYs]

    # initialize gradient outputs
    dXs = [numpy.zeros(s, dy.dtype) for s, dy in zip(X_shape, dYs)]

    # prepare axis selection
    axis, deform_shape = _normalize_axis_list(axis, dXs)

    # prepare cropping
    output_shapes, output_offset = _compute_output_shapes(dXs, axis, deform_shape, crop)
    if [tuple(s) for s in output_shapes] != [dy.shape for dy in dYs]:
        raise ValueError("X_shape does not match output shape and cropping. "
                         "Expected output shape is %s, but %s given."
                         % (str(output_shapes), str([dy.shape for dy in dYs])))

    # prepare other parameters
    displacement = _normalize_displacement(displacement, dYs, axis)
    order = _normalize_order(order, dYs)
    mode = _normalize_mode(mode, dYs)
    cval = _normalize_cval(cval, dYs)
    affine = _normalize_affine(affine, axis)

    # compute inverse affine given output affine
    inverse_affine = _compute_inverse_affine(affine)

    # add rotation and zoom to the affine matrix
    inverse_affine = _apply_rotation_and_zoom(rotate, zoom, inverse_affine, [output_shapes[0][d] for d in axis[0]])

    # prefilter displacement
    displacement_f = numpy.zeros_like(displacement)
    for d in range(1, displacement.ndim):
        scipy.ndimage.spline_filter1d(displacement, axis=d, order=3, output=displacement_f)
        displacement = displacement_f

    _deform_grid.deform_grid_grad(dXs, displacement_f, output_offset, dYs, axis, order, mode, cval, inverse_affine)

    # compute gradient of prefilter operation
    dXs_f = []
    for i, x in enumerate(dXs):
        if prefilter and order[i] > 1:
            x_f = numpy.zeros_like(x)
            for d in axis[i]:
                _deform_grid.spline_filter1d_grad(x, x_f, d, order[i])
                x = x_f
            dXs_f.append(x_f)
        else:
            dXs_f.append(x)

    if isinstance(dY, list):
        return dXs_f
    else:
        return dXs_f[0]



def _normalize_inputs(X):
    if isinstance(X, numpy.ndarray):
        Xs = [X]
    elif isinstance(X, list):
        Xs = X
    else:
        raise Exception('X should be a numpy.ndarray or a list of numpy.ndarrays.')

    # check X inputs
    assert len(Xs) > 0, 'You must provide at least one image.'
    assert all(isinstance(x, numpy.ndarray) for x in Xs), 'All elements of X should be numpy.ndarrays.'
    return Xs

def _normalize_axis_list(axis, Xs):
    if axis is None:
        axis = [tuple(range(x.ndim)) for x in Xs]
    elif isinstance(axis, int):
        axis = (axis,)
    if isinstance(axis, tuple):
        axis = [axis] * len(Xs)
    assert len(axis) == len(Xs), 'Number of axis tuples should match number of inputs.'
    input_shapes = []
    for x, ax in zip(Xs, axis):
        assert isinstance(ax, tuple), 'axis should be given as a tuple'
        assert all(isinstance(a, int) for a in ax), 'axis must contain ints'
        assert len(ax) == len(axis[0]), 'All axis tuples should have the same length.'
        assert ax == tuple(set(ax)), 'axis must be sorted and unique'
        assert all(0 <= a < x.ndim for a in ax), 'invalid axis for input'
        input_shapes.append(tuple(x.shape[d] for d in ax))
    assert len(set(input_shapes)) == 1, 'All inputs should have the same shape.'
    deform_shape = input_shapes[0]
    return axis, deform_shape

def _compute_output_shapes(Xs, axis, deform_shape, crop):
    if crop is not None:
        assert isinstance(crop, (tuple, list)), "crop must be a tuple or a list."
        assert len(crop) == len(deform_shape)
        output_shapes = [list(x.shape) for x in Xs]
        output_offset = [0 for d in range(len(axis[0]))]
        for d in range(len(axis[0])):
            if isinstance(crop[d], slice):
                assert crop[d].step is None
                start = (crop[d].start or 0)
                stop = (crop[d].stop or deform_shape[d])
                assert start >= 0
                assert start < stop and stop <= deform_shape[d]
                for i in range(len(Xs)):
                    output_shapes[i][axis[i][d]] = stop - start
                if start > 0:
                    output_offset[d] = start
            else:
                raise Exception('Crop must be a slice.')
        if any(o > 0 for o in output_offset):
            output_offset = numpy.array(output_offset).astype('int64')
        else:
            output_offset = None
    else:
        output_shapes = [x.shape for x in Xs]
        output_offset = None
    return output_shapes, output_offset

def _normalize_displacement(displacement, Xs, axis):
    assert isinstance(displacement, numpy.ndarray), 'Displacement matrix should be a numpy.ndarray.'
    assert displacement.ndim == len(axis[0]) + 1, 'Number of dimensions of displacement does not match input.'
    assert displacement.shape[0] == len(axis[0]), 'First dimension of displacement should match number of input dimensions.'
    return displacement

def _normalize_order(order, Xs):
    if not isinstance(order, (tuple, list)):
        order = [order] * len(Xs)
    assert len(Xs) == len(order), 'Number of order parameters should be equal to number of inputs.'
    assert all(0 <= o and o <= 5 for o in order), 'order should be 0, 1, 2, 3, 4 or 5.'
    return numpy.array(order).astype('int64')

def _normalize_mode(mode, Xs):
    if not isinstance(mode, (tuple, list)):
        mode = [mode] * len(Xs)
    mode = [_extend_mode_to_code(o) for o in mode]
    assert len(Xs) == len(mode), 'Number of mode parameters should be equal to number of inputs.'
    return numpy.array(mode).astype('int64')

def _normalize_cval(cval, Xs):
    if not isinstance(cval, (tuple, list)):
        cval = [cval] * len(Xs)
    assert len(Xs) == len(cval), 'Number of cval parameters should be equal to number of inputs.'
    return numpy.array(cval).astype('float64')

def _normalize_affine(affine, axis):
    if affine is None:
        return affine
    n_axes = len(axis[0])
    if affine.shape == (n_axes + 1, n_axes + 1):
        assert numpy.allclose(affine[n_axes, :], [0, 0, 1]), 'Invalid affine matrix.'
        affine = affine[:n_axes, :]
    assert affine.shape == (n_axes, n_axes + 1), 'Affine matrix should have shape (ndim, ndim+1).'
    return numpy.array(affine).astype('float64')

def _compute_inverse_affine(affine):
    if affine is None:
        return None
    else:
        inverse_affine = numpy.zeros(affine.shape, dtype='float64')
        inverse_affine[:, :-1] = numpy.linalg.inv(affine[:, :-1])
        inverse_affine[:, -1] = -numpy.dot(inverse_affine[:, :-1], affine[:, -1])
        return inverse_affine

def _compute_rotation_zoom_affine(angle=None, zoom=None, center=None):
    affine = None
    if center is not None:
        a = numpy.array([[1, 0, -center[0]],
                         [0, 1, -center[1]],
                         [0, 0, 1]])
        affine = a if affine is None else numpy.dot(a, affine)
    if angle:
        theta = numpy.radians(angle)
        a = numpy.array([[numpy.cos(theta), -numpy.sin(theta), 0],
                         [numpy.sin(theta),  numpy.cos(theta), 0],
                         [0, 0, 1]])
        affine = a if affine is None else numpy.dot(a, affine)
    if zoom:
        a = numpy.array([[zoom, 0, 0],
                         [0, zoom, 0],
                         [0, 0, 1]])
        affine = a if affine is None else numpy.dot(a, affine)
    if center is not None:
        a = numpy.array([[1, 0, center[0]],
                         [0, 1, center[1]],
                         [0, 0, 1]])
        affine = a if affine is None else numpy.dot(a, affine)
    return affine

def _apply_rotation_and_zoom(rotate, zoom, inverse_affine, output_shape):
    if rotate is None and zoom is None:
        return inverse_affine
    assert len(output_shape) == 2, 'Zoom and rotate is only implemented for 2D images.'
    rotate = -float(rotate or 0)
    zoom = 1 / float(zoom or 1)
    new_inverse_affine = _compute_rotation_zoom_affine(angle=rotate, zoom=zoom, center=numpy.array(output_shape) / 2 - 0.5)
    if inverse_affine is not None:
        base_inverse_affine = numpy.eye(3, dtype='float64')
        base_inverse_affine[:-1, :] = inverse_affine
        return numpy.dot(new_inverse_affine, base_inverse_affine)[:2, :]
    else:
        return new_inverse_affine[:2, :]

def _extend_mode_to_code(mode):
    """Convert an extension mode to the corresponding integer code.
    """
    if mode == 'nearest':
        return 0
    elif mode == 'wrap':
        return 1
    elif mode == 'reflect':
        return 2
    elif mode == 'mirror':
        return 3
    elif mode == 'constant':
        return 4
    else:
        raise RuntimeError('boundary mode not supported')

