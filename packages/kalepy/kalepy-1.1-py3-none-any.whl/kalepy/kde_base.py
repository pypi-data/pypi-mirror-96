"""
"""
import logging
import six

import numpy as np
import scipy as sp

from kalepy import kernels, utils, _NUM_PAD
from kalepy import _BANDWIDTH_DEFAULT

__all__ = ['KDE']


class KDE(object):
    """Core class and primary API for using `Kalepy`, by constructin a KDE based on given data.

    The `KDE` class acts as an API to the underlying `kernel` structures and methods.  From the
    passed data, a 'bandwidth' is calculated and/or set (using optional specifications using the
    `bandwidth` argument).  A `kernel` is constructed (using optional specifications in the
    `kernel` argument) which performs the calculations of the kernel density estimation.


    Notes
    -----
    Reflection ::

        Reflective boundary conditions can be used to better reconstruct a PDF that is known to
        have finite support (i.e. boundaries outside of which the PDF should be zero).

        The `pdf` and `resample` methods accept the keyword-argument (kwarg) `reflect` to specify
        that a reflecting boundary should be used.

        reflect : (D,) array_like, None (default)
            Locations at which reflecting boundary conditions should be imposed.
            For each dimension `D`, a pair of boundary locations (for: lower, upper) must be
            specified, or `None`.  `None` can also be given to specify no boundary at that
            location.

            If a pair of boundaries are given, then the
            first value corresponds to the lower boundary, and the second value to the upper
            boundary, in that dimension.  If there should only be a single lower or upper
            boundary, then `None` should be passed as the other boundary value.

        Example:
           ```reflect=[None, [-1.0, 1.0], [0.0, None]]```
        specifies that the 0th dimension has no boundaries, the 1st dimension has
        boundaries at both -1.0 and 1.0, and the 2nd dimension has a lower boundary at 0.0,
        and no upper boundary.

    Projection / Marginalization ::

        The PDF can be calculated for only particular parameters/dimensions.
        The `pdf` method accepts the keyword-argument (kwarg) `params` to specify particular
        parameters over which to calculate the PDF (i.e. the other parameters are projected over).

        params : int, array_like of int, None (default)
            Only calculate the PDF for certain parameters (dimensions).

            If `None`, then calculate PDF along all dimensions.
            If `params` is specified, then the target evaluation points `pnts`, must only
            contain the corresponding dimensions.

        Example:
        If the `dataset` has shape (4, 100), but `pdf` is called with `params=(1, 2)`,
        then the `pnts` array should have shape `(2, M)` where the two provides dimensions
        correspond to the 1st and 2nd variables of the `dataset`.

    TODO: add notes on `keep` parameter

    Dynamic Range ::

        When the elements of the covariace matrix between data variables differs by numerous
        orders of magnitude, the KDE values (especially marginalized values) can become spurious.
        One solution is to use a diagonal covariance matrix by initializing the KDE instance with
        `diagonal=True`.  An alternative is to transform the input data in such a way that each
        variable's dynamic range becomes similar (e.g. taking the log of the values).  A warning
        is given if the covariance matrix has a large dynamic very-large dynamic range, but no
        error is raised.

    Examples
    --------
    Construct semi-random data:

    >>> import numpy as np
    >>> np.random.seed(1234)
    >>> data = np.random.normal(0.0, 1.0, 1000)

    Construct `KDE` instance using this data, and the default bandwidth and kernels.

    >>> import kalepy as kale
    >>> kde = kale.KDE(data)

    Compare original PDF and the data to the reconstructed PDF from the KDE:

    >>> xx = np.linspace(-3, 3, 400)
    >>> pdf_tru = np.exp(-xx*xx/2) / np.sqrt(2*np.pi)
    >>> pdf_kde = kde.pdf(xx)

    >>> import matplotlib.pyplot as plt
    >>> ll = plt.plot(xx, pdf_tru, 'k--', label='Normal PDF')
    >>> _, bins, _ = plt.hist(data, bins=14, density=True, \
                              color='0.5', rwidth=0.9, alpha=0.5, label='Data')
    >>> ll = plt.plot(xx, pdf_kde, 'r-', label='KDE')
    >>> ll = plt.legend()

    Compare the KDE reconstructed PDF to the "true" PDF, make sure the chi-squared is consistent:

    >>> dof = xx.size - 1
    >>> x2 = np.sum(np.square(pdf_kde - pdf_tru)/pdf_tru**2)
    >>> x2 = x2 / dof
    >>> x2 < 0.1
    True
    >>> print("Chi-Squared: {:.1e}".format(x2))
    Chi-Squared: 1.7e-02

    Draw new samples from the data and make sure they are consistent with the original data:

    >>> import scipy as sp
    >>> samp = kde.resample()
    >>> ll = plt.hist(samp, bins=bins, density=True, color='r', alpha=0.5, rwidth=0.5, \
                      label='Samples')
    >>> ks, pv = sp.stats.ks_2samp(data, samp)
    >>> pv > 0.05
    True
    >>> print("p-value: {:.1e}".format(pv))
    p-value: 9.5e-01

    """

    def __init__(self, dataset, bandwidth=None, weights=None, kernel=None,
                 neff=None, diagonal=False, helper=True, bw_rescale=None, **kwargs):
        """Initialize the `KDE` class with the given dataset and optional specifications.

        Arguments
        ---------
        dataset : array_like (N,) or (D,N,)
            Dataset from which to construct the kernel-density-estimate.
            For multivariate data with `D` variables and `N` values, the data must be shaped (D,N).
            For univariate (D=1) data, this can be a single array with shape (N,).

        bandwidth : str, float, array of float, None  [optional]
            Specification for the bandwidth, or the method by which the bandwidth should be
            determined.  If a `str` is given, it must match one of the standard bandwidth
            determination methods.  If a `float` is given, it is used as the bandwidth in each
            dimension.  If an array of `float`s are given, then each value will be used as the
            bandwidth for the corresponding data dimension.
        weights : array_like (N,), None  [optional]
            Weights corresponding to each `dataset` point.  Must match the number of points `N` in
            the `dataset`.
            If `None`, weights are uniformly set to 1/N for each value.
        kernel : str, Distribution, None  [optional]
            The distribution function that should be used for the kernel.  This can be a `str`
            specification that must match one of the existing distribution functions, or this can
            be a `Distribution` subclass itself that overrides the `_evaluate` method.
        neff : int, None  [optional]
            An effective number of datapoints.  This is used in the plugin bandwidth determination
            methods.
            If `None`, `neff` is calculated from the `weights` array.  If `weights` are all
            uniform, then `neff` equals the number of datapoints `N`.
        diagonal : bool,
            Whether the bandwidth/covariance matrix should be set as a diagonal matrix
            (i.e. without covariances between parameters).
            NOTE: see `KDE` docstrings, "Dynamic Range".

        """
        self._helper = helper
        self._dataset = np.atleast_2d(dataset)
        ndim, ndata = self.dataset.shape
        if weights is None:
            weights = np.ones(ndata)/ndata
        bw_method = kwargs.pop('bw_method', None)
        if bw_method is not None:
            logging.info("Use `bandwidth` argument instead of `bw_method`")
            if bandwidth is not None:
                err = "Use only the `bandwidth` argument, not `bw_method` also!"
                raise ValueError(err)
            bandwidth = bw_method
            del bw_method

        if bandwidth is None:
            bandwidth = _BANDWIDTH_DEFAULT

        self._diagonal = diagonal
        self._ndim = ndim
        self._ndata = ndata

        if np.count_nonzero(weights) == 0 or np.any(~np.isfinite(weights) | (weights < 0)):
            raise ValueError("Invalid `weights` entries, all must be finite and > 0!")
        weights = np.atleast_1d(weights).astype(float)
        weights /= np.sum(weights)
        if np.shape(weights) != (ndata,):
            raise ValueError("`weights` input should be shaped as (N,)!")

        self._weights = weights

        if neff is None:
            neff = 1.0 / np.sum(weights**2)

        self._neff = neff

        covariance = np.cov(dataset, rowvar=True, bias=False, aweights=weights)
        self._covariance = np.atleast_2d(covariance)
        self._set_bandwidth(bandwidth, bw_rescale)

        # Convert from string, class, etc to a kernel
        dist = kernels.get_distribution_class(kernel)
        self._kernel = kernels.Kernel(
            distribution=dist, bandwidth=self._bandwidth, covariance=self._covariance,
            helper=helper, **kwargs)

        self._finalize()
        self._cdf_grid = None
        self._cdf_func = None
        return

    def _guess_edges(self, nmin=100, nmax=1e4, tot_max=1e8, reflect=None):
        """Guess good grid edges to resolve the KDE's PDF.

        To-Do: this doesn't need to be done on a grid, do something smarter!
        To-Do: implement reflect (set boundaries to reflect values when given)

        """
        data = self.dataset
        neff = self.neff
        ndim = self.ndim
        bandwidth = self.kernel.bandwidth.diagonal()
        finite = self.kernel.FINITE
        if reflect is not None:
            raise ValueError("`reflect` is not supported in calculing grid edges!")

        # Number of grid points in each dimension
        max_per_dim = np.power(tot_max, 1.0/ndim)
        if max_per_dim < nmin:
            err = (
                "Cannot resolve ndim={} dimensions ".format(ndim) +
                "with at least nmin={:.2e} ".format(nmin) +
                "points and stay below maximum = {:.3e}!".format(tot_max)
            )
            raise ValueError(err)

        npd = np.power(neff, 1.0/ndim)
        npd = np.clip(npd, nmin, nmax)
        npd = np.clip(npd, 0.0, max_per_dim)
        npd = int(npd)
        msg = "KDE._guess_edges:: Using {} bins per dimension".format(npd)
        # print(msg)
        if self._helper:
            logging.info(msg)

        # If the Kernel is finite, then there is only support out to `bandwidth` beyond extrema
        if finite:
            out = (1.0 + _NUM_PAD)
        # If infinite, how many standard-deviations can we expect data points to lie at
        else:
            out = sp.stats.norm.ppf(1 - 1/neff)
            # Extra to be double sure...
            out *= 1.5

        # Find the extrema in each dimension
        extr = [[np.min(dd) - bw*out, np.max(dd) + bw*out] for bw, dd in zip(bandwidth, data)]
        edges = [np.linspace(*ex, npd) for ex in extr]
        msg = "KDE._guess_edges:: extrema = {}".format(
            ", ".join(["[{:.2e}, {:.2e}]".format(*ex) for ex in extr]))
        # print(msg)

        return edges

    def pdf(self, pnts, reflect=None, params=None):
        """Evaluate the kernel-density-estimate PDF at the given data-points.

        This method acts as an API to the `Kernel.pdf` method of this instance's `kernel`.

        Arguments
        ---------
        pnts : ([D,]M,) array_like of float
            The locations at which the PDF should be evaluated.  The number of dimensions `D` must
            match that of the `dataset` that initialized this class' instance.
            NOTE: If the `params` kwarg (see below) is given, then only those dimensions of the
            target parameters should be specified in `pnts`.

        reflect : (D,) array_like, None (default)
            Locations at which reflecting boundary conditions should be imposed.
            For each dimension `D`, a pair of boundary locations (for: lower, upper) must be
            specified, or `None`.  `None` can also be given to specify no boundary at that
            location.  See class docstrings:`Reflection` for more information.
        params : int, array_like of int, None (default)
            Only calculate the PDF for certain parameters (dimensions).
            See class docstrings:`Projection` for more information.

        """
        result = self.kernel.pdf(pnts, self.dataset, self.weights, reflect=reflect, params=params)
        # print("KDE.pdf(): result.shape = {}".format(result.shape))
        return result

    def pdf_grid(self, edges, reflect=None, params=None):
        """Convenience method to compute the PDF given the edges of a grid in each dimension.

        Arguments
        ---------
        edges : (D,) arraylike of arraylike
            The edges defining a regular grid to use as points when calculating PDF values.
            These edges are used with `numpy.meshgrid` to construct the grid points.

            Example:
            If the KDE is initialized with a 3-parameter dataset [i.e. (3,N)], then `edges`
            must be a list of three arrays, each specifying the grid-points along the corresponding
            parameter.  Define the lengths of each array as: A, B, C; then the grid and the
            returned PDF will have a shape (A, B, C).

        reflect : (D,) array_like, None (default)
            Locations at which reflecting boundary conditions should be imposed.
            For each dimension `D`, a pair of boundary locations (for: lower, upper) must be
            specified, or `None`.  `None` can also be given to specify no boundary at that
            location.  See class docstrings:`Reflection` for more information.

        params : int, array_like of int, None (default)
            Only calculate the PDF for certain parameters (dimensions).
            See class docstrings:`Projection` for more information.

        """
        ndim = self.ndim
        # If `edges` is 1D (and not "jagged") then expand to 2D
        if utils.really1d(edges):
            edges = np.atleast_2d(edges)

        # Check shape if unput `edges`
        if (params is None):
            # Should be edges for all parameters
            if len(edges) != ndim:
                err = "`edges` must be (D,)=({},): an arraylike of edges for each dim/param!"
                err = err.format(ndim)
                raise ValueError(err)
        else:
            # Should only be as many edges as target parameters
            if np.size(params) != len(edges):
                err = "`params` = '{}' (length {}), but length of `edges` = {}!".format(
                    params, len(params), len(edges))
                raise ValueError(err)

        coords = np.meshgrid(*edges, indexing='ij')
        shp = np.shape(coords)[1:]
        coords = np.vstack([xx.ravel() for xx in coords])
        pdf = self.pdf(coords, reflect=reflect, params=params)
        pdf = pdf.reshape(shp)
        # print("KDE.pdf_grid(): result.shape = {}".format(pdf.shape))
        return pdf

    def cdf(self, pnts):
        """Cumulative Distribution Function based on KDE smoothed data.

        Arguments
        ---------
        pnts : ([D,]N,) array_like of scalar
            Target evaluation points

        Returns
        -------
        cdf : (N,) ndarray of scalar
            CDF Values at the target points

        """
        if self._cdf_func is None:
            edges = self._guess_edges()

            # Calculate PDF at grid locations
            pdf = self.pdf_grid(edges)
            # Convert to CDF using trapezoid rule
            cdf = utils.cumtrapz(pdf, edges)
            # Normalize to the maximum value
            cdf /= cdf.max()

            self._cdf_grid = (edges, cdf)
            self._cdf_func = sp.interpolate.RegularGridInterpolator(
                *self._cdf_grid, bounds_error=False, fill_value=None)

        # `scipy.interplate.RegularGridInterpolator` expects shape (N,D,) -- so transpose
        pnts = np.asarray(pnts).T
        cdf = self._cdf_func(pnts)
        return cdf

    def cdf_grid(self, edges, **kwargs):
        ndim = self.ndim
        if len(edges) != ndim:
            err = "`edges` must be (D,)=({},): an arraylike of edges for each dim/param!"
            err = err.format(ndim)
            raise ValueError(err)

        coords = np.meshgrid(*edges, indexing='ij')
        shp = np.shape(coords)[1:]
        coords = np.vstack([xx.ravel() for xx in coords])
        cdf = self.cdf(coords, **kwargs)
        cdf = cdf.reshape(shp)
        return cdf

    def resample(self, size=None, keep=None, reflect=None, squeeze=True):
        """Draw new values from the kernel-density-estimate calculated PDF.

        The KDE calculates a PDF from the given dataset.  This method draws new, semi-random data
        points from that PDF.

        Arguments
        ---------
        size : int, None (default)
            The number of new data points to draw.  If `None`, then the number of `datapoints` is
            used.

        keep : int, array_like of int, None (default)
            Parameters/dimensions where the original data-values should be drawn from, instead of
            from the reconstructed PDF.
            TODO: add more information.
        reflect : (D,) array_like, None (default)
            Locations at which reflecting boundary conditions should be imposed.
            For each dimension `D`, a pair of boundary locations (for: lower, upper) must be
            specified, or `None`.  `None` can also be given to specify no boundary at that
            location.
        squeeze : bool, (default: True)
            If the number of dimensions `D` is one, then return an array of shape (L,) instead of
            (1, L).

        Returns
        -------
        samples : ([D,]L) ndarray of float
            Newly drawn samples from the PDF, where the number of points `L` is determined by the
            `size` argument.
            If `squeeze` is True (default), and the number of dimensions in the original dataset
            `D` is one, then the returned array will have shape (L,).

        """
        samples = self.kernel.resample(
            self.dataset, self.weights,
            size=size, keep=keep, reflect=reflect, squeeze=squeeze)
        return samples

    # def ppf(self, cfrac):
    #     return self.kernel.ppf(cfrac)

    def _finalize(self, log_ratio_tol=5.0):
        WARN_ALL_BELOW = -10
        EXTR_ABOVE = -20

        mat = self.kernel.matrix
        ndim = self._ndim
        # Diagonal elements of the matrix
        diag = mat.diagonal()

        # Off-diagonal matrix elements
        ui = np.triu_indices(ndim, 1)
        li = np.tril_indices(ndim, -1)
        offd = np.append(mat[ui], mat[li])

        warn = False

        if np.any(offd != 0.0):
            d_vals = np.log10(np.fabs(diag))
            o_vals = np.log10(np.fabs(offd))
            if np.all(d_vals <= WARN_ALL_BELOW) and np.all(o_vals <= WARN_ALL_BELOW):
                logging.warning("Covariance matrix:\n" + str(mat))
                logging.warning("All matrix elements are less than 1e{}!".format(WARN_ALL_BELOW))
                warn = True

            d_extr = utils.minmax(d_vals[d_vals > EXTR_ABOVE])
            o_extr = utils.minmax(o_vals[o_vals > EXTR_ABOVE])

            ratio = np.fabs(d_extr[:, np.newaxis] - o_extr[np.newaxis, :])
            if np.any(ratio >= log_ratio_tol):
                logging.warning("Covariance matrix:\n" + str(mat))
                msg = "(log) Ratio of covariance elements ({}) exceeds tolerance ({})!".format(
                    ratio, log_ratio_tol)
                logging.warning(msg)
                warn = True

        if warn:
            msg = "Recommend rescaling input data, or using a diagonal covariance matrix"
            logging.warning(msg)

        return

    # ==== Properties ====

    @property
    def bandwidth(self):
        return self._bandwidth

    @property
    def covariance(self):
        return self._covariance

    @property
    def dataset(self):
        return self._dataset

    @property
    def kernel(self):
        return self._kernel

    @property
    def ndata(self):
        return self._ndata

    @property
    def ndim(self):
        return self._ndim

    @property
    def neff(self):
        return self._neff

    @property
    def weights(self):
        return self._weights

    # ==== BANDWIDTH ====

    def _set_bandwidth(self, bw_input, bw_rescale):
        ndim = self.ndim
        bandwidth = np.zeros((ndim, ndim))

        if len(np.atleast_1d(bw_input)) == 1:
            _bw, method = self._compute_bandwidth(bw_input)
            if not self._diagonal:
                bandwidth[...] = _bw
            else:
                idx = np.arange(ndim)
                bandwidth[idx, idx] = _bw
        else:
            if np.shape(bw_input) == (ndim,):
                # bw_method = 'diagonal'
                for ii in range(ndim):
                    bandwidth[ii, ii], *_ = self._compute_bandwidth(
                        bw_input[ii], param=(ii, ii))
                method = 'diagonal'
            elif np.shape(bw_input) == (ndim, ndim):
                for ii, jj in np.ndindex(ndim, ndim):
                    bandwidth[ii, jj], *_ = self._compute_bandwidth(
                        bw_input[ii, jj], param=(ii, jj))
                method = 'matrix'
            else:
                err = "`bandwidth` must have shape (1,), (N,) or (N,N,) for `N` dimensions!"
                raise ValueError(err)

        if self._helper and np.any(np.isclose(bandwidth.diagonal(), 0.0)):
            ii = np.where(np.isclose(bandwidth.diagonal(), 0.0))[0]
            msg = "WARNING: diagonal '{}' of bandwidth is near zero!".format(ii)
            logging.warning(msg)

        # Rescale the bandwidth matrix
        if bw_rescale is not None:
            bwr = np.atleast_2d(bw_rescale)
            bandwidth = bwr * bandwidth
            if self._helper:
                logging.info("Rescaling `bw_white_matrix` by '{}'".format(
                    bwr.squeeze().flatten()))

        # bw_matrix = self._data_cov * (bw_white_matrix ** 2)
        self._bandwidth = bandwidth

        # prev: bw_white
        # self._bw_white_matrix = bw_white_matrix
        self._method = method
        # self._bw_input = bw_input
        # prev: bw_cov
        # self._bw_matrix = bw_matrix
        return

    def _compute_bandwidth(self, bandwidth, param=None):
        if isinstance(bandwidth, six.string_types):
            if bandwidth == 'scott':
                bw = self._scott_factor(param=param)
            elif bandwidth == 'silverman':
                bw = self._silverman_factor(param=param)
            else:
                msg = "Unrecognized bandwidth str specification '{}'!".format(bandwidth)
                raise ValueError(msg)

            method = bandwidth

        elif np.isscalar(bandwidth):
            bw = bandwidth
            method = 'constant scalar'

        else:
            raise ValueError("Unrecognized `bandwidth` '{}'!".format(bandwidth))

        '''
        elif callable(bandwidth):
            bw = bandwidth(self, param=param)
            method = 'function'
            bw_cov = 1.0
        '''

        return bw, method

    def _scott_factor(self, *args, **kwargs):
        return np.power(self.neff, -1./(self.ndim+4))

    def _silverman_factor(self, *args, **kwargs):
        return np.power(self.neff*(self.ndim+2.0)/4.0, -1./(self.ndim+4))
