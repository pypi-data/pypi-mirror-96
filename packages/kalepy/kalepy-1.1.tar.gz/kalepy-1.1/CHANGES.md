## To-Do / Known-Issues
- **Optimization needed**.  Things are done in (generally) the simplest ways, currently, need to be optimized for performance (both speed and memory [e.g. with reflections]).  Especially in the case of finite-support kernels, the calculations can be drastically sped up.  Can also use an approximation for infinite-support kernels, truncating at some threshold value of sigma (or percentile; etc).
- Try using `sp.stats.rv_continuous` as base-class for 'Distribution' to provide functionality like 'ppf' etc.
- Differences between covariance-matrix elements of numerous orders of magnitude can cause spurious results, in particular in the PDF marginalized over parameters.  See "KDE::Dynamic Range" docstrings.  Currently this is checked for in the `KDE._finalize()` method, at the end of initialization, and a warning is given if the dynamic range seems too large.
- Move all checking/sanitizing functionality to `KDE` and have `kernels` (etc) assume it's correct.
  - e.g. extrema, points, reflection, params, etc
- Add documenation/examples for base drawing functions in plotting submodule (e.g. `draw_contour2d`, `draw_hist1d`, etc).


- `kalepy/`
    - Allow for calculating PDF and resampling in only particular dimensions/parameters.
        - FIX: Doesn't work quite right for non-fixed bandwidth, bandwidth needs to be re-calculated for different number of dimensions
    - `tests/`
        - No tests currently check that proper errors are raised.
        - Make sure tests check both cases of `num_points > num_data` and visa-versa (e.g. in PDF calculation).
    - `kernels.py`
        - See if `_resample_clear` and `_resample_reflect` can be combined.
    - `kde.py`
      - `KDE`
        - Explore more efficient ways of calculating the CDF using the underlying kernels instead of integrating the PDF.
        - Use different methods for `grid` edges in ND, instead of broadcasting and flattening (inefficient).


## v1.1 - 2021/03/02

- Allow `covariance` to be manually specified in KDE constructor.
- New `KDE.from_hist()` method for constructing KDEs based on existing distributions (instead of finite points).
- Deprecated CDF functionality removed (for the time being).
- `Triweight` distribution works.
- Significant PDF evaluation speed improvements using numba
  - Sampling and evaluation code simplified.
- Use `abc.ABC` base classes
  - `Distribution(object)` ==> `_Distribution(abc.ABC)`
- Plotting improvements
  - BUG: fix incorrect label in rotate bottom-right panels of corner plots
  - Allow `target` lines to be drawn on corner plots using `Corner.target()`
  - Add arguments to limit the number of carpet and scatter points drawn


## v1.0.0 - 2021/01/21

- DOCS: significant expansion of documentation, both docstrings and sphinx (readthedocs.org).
- Allow `kale.plot.Corner` instances to accept externally-created axes.
- Simplify handling of `reflect` arguments.
- Improve bin-edge guessing.


## v0.5 - 2020/12/30

- Complete restructure of `kalepy.plot` submodule, particularly in the API.
- Extensive addition and improvements of documentation, both inline docstrings, and the addition of sphinx docs now available on [kalepy.readthedocs.io](kalepy.readthedocs.io).
  - This includes new demo/test notebooks which are automatically incorporated into the `README.md` and sphinx documentation.
  - Documentation, testing, and examples are now included for core plotting functionality.  More is needed for the base drawing functions (e.g. `draw_contour2d`, `draw_hist1d`, etc)
- `kalepy` paper
  - Fixed typos pointed out by JOSS referees.
  - Added citation and comparison to `GetDist` package.
- BUG: `weights` was not being passed correctly during resampling (without reflection).
- MAINT: fixed a huge number of deprecation warnings now raised by numpy about operations on jagged arrays.
  - Improved functionality of `kale.utils.jshape` and `kale.utils.really1d` functions to accommodate.
- General plotting improvements
  - The handling of colors and colormaps: plotting methods will automatically select the next colorcycle color, construct a matching colormap, and synchronize the color of all plot components.
  - The handling of quantiles for confidence and contour components: are now handles much more self-consistently and with a simpler API.
  - Drawing functions (e.g. `carpet`, `dist1d` and `dist2d`) will load the current, active axes by default.


## v0.4 - 2020/10/12

- Added paper submitted to JOSS


## v0.3.3 - 2020/07/27

- API:
  - Removed `KDE.pdf_grid` method, instead use `KDE.pdf(... grid=True)`.
  - `KDE.pdf(...)` just calls `KDE.density(..., probability=True)`
    - NOTE: this means that, like `density` the `pdf()` function now returns a (2,) tuple of the evaluation points in addition to the density values!
  - The arguments `reflect` and `params` can now be used in tandem.

- `kalepy/`
  - `kde.py`
    - `KDE`
      - `pdf(...)` is now identical to `density(..., probability=True)`
      - `pdf_grid()` [DELETED]
        - Call `pdf(..., grid=True)` instead.
  - `kernels.py`
    - `Kernel`
      - `density()` <== `pdf`, `_pdf_clear`, and `_pdf_reflect`
        - Combined latter functions into single new method.



## v0.3.2 - 2020/06/08

- `reflect` arguments: `True` can now be given (single value, or for a particular parameter/dimension), in which case the KDE will guess the reflection points based on the data extrema (in all dimensions, or only the target ones).  This happens in `kernels._check_reflect`.
- General bug fixes.
- Improve kwarg handling in plotting.

- API
  - `kalepy.density()`
    - BUG: fixed issue in 'grid' mode where output points didn't match values in shape.
    - Add `grid` kwarg.

- `kalepy/`
  - `kernels.py`
    - `_check_reflect()`
      - Added boolean functionality for `reflect` arguments, which are then replaced with data extrema as needed.
  - `plot.py`
    - General bug fixes, improvements in kwarg handling.
    - Return `handles` from plotting functions to allow for legends.
  - `utils.py`
    - New methods for checking / handling jagged arrays (`flatten()`, `flatlen()`, `isjagged()` and `jshape`)

- `notebooks/`
  - `api.ipynb`  [NEW-FILE]
    - New notebook for running API tests.

- `gen_readme.py`  [NEW-FILE]
  - Script to automatically assemble the `README.md` file based on an input template `_README.md` and the jupyter notebook `demo.ipynb`.  Automatically takes care of image files, and updating them with git.
- `README.md`
  - Updated (using `gen_readme.py`) to include new, cleaner examples (primarily using top-level API).


## v0.3.1 - 2020/04/30
- Improved how 'edges' (both for bins and PDF evaluation) are constructed, especially in multiple dimensions.  `KDE` constructs extrema from the given data and then calls `utils.parse_edges`.

- `kalepy/`
  - `__init__.py`
    - `corner()`  [NEW-METHOD]
      - New top-level API method for constructing corner plots using either a dataset or KDE instance.
    - `density()`  [NEW-METHOD]
      - Interface to `KDE.density()`
    - `resample()`  [NEW-METHOD]
      - Interface to `KDE.resample()`
  - `kde.py`  <==  `kde_base.py`  [RENAME]
    - Improved how 'edges' are constructed.  Constructs `extrema` based on input data, and uses `utils.parse_edges` to construct edges.
    - `_guess_edges()`  [REMOVED]
    - `KDE`
      - `density()`  [NEW-METHOD]
        - Calculate density using KDE, where 'density' can either be number density or probability density (i.e. 'pdf').
      - `pdf()`
        - Now calls `density()` using `probability=True`.
  - `kernels.py`
  - `plot.py`
    - Methods for constructing "corner" plots (based strongly on Dan Foreman-Mackey's `corner` package).
    - `Corner`
      - Class for managing corner plots and plotting scatter data or KDE PDFs.

    - `corner_data()`
      - Higher-level function for constructing a full corner plot given scatter-data.
    - `draw_carpet()`  <==  `draw_carpet_fuzz()`  [RENAME]
      - Add `rotate` argument to plot vertically instead of horizontally.
    - `hist()` [NEW-METHOD]
      - Calculate histogram using `utils.histogram()`, then draw it using `_draw_hist1d()`.
    - `utils()`
      - Add `positive` argument to filter by positive definite values.
    - `_get_smap()`  <==  `smap()`  [RENAME]
      - Add `log` argument to specify log-scaling.
  - `utils.py`
    - `histogram()`  [NEW-METHOD]
      - Calculate histograms with both `density` and `probability` parameters (instead of combined like in numpy).
    - `parse_edges()`
      - Allow `weights` to be passed for calculating effective number of data points and inter-quartile ranges
    - `quantiles()`  <==  `percentiles()`
    - `stats()`  [NEW-METHOD]
      - Combines `array_str()` and `stats_str()` output.
    - `_get_edges_1d()`
      - BUG: avoid negative bin-width for very small number of data points.

- `notebooks/`
  - `plotting.ipynb`  [NEW-FILE]
    - For testing and demonstration of plotting methods, especially corner plots.
  - `kde.ipynb`
    - Add corner plots using the `corner.py` submodule.

- `convert_notebook_tests.py`  <==  `build_notebook_tests.py`  [RENAME]



## v0.3.0 - 2020/04/07

- Started working on cleaning up the API (i.e. outward visible functions and structures).
  - New API Functions: `kalepy.pdf()`, `kalepy.cdf()`
- Cleanup variable naming conventions in KDE and Kernels.

- BUG: calculating PDF with `params` given would often result in an error from bad checking of edges/grid shapes.

- `kalepy/`
  - `__init__.py`
    - `pdf()`  [NEW-METHOD]
      - Convenience / API Method for constructing a quick PDF based on the given data.
    - `cdf()`  [NEW-METHOD]
      - Convenience / API Method for constructing a quick CDF based on the given data.
  - `kde_base.py`
    - `KDE`
      - BUG: when providing a scalar value for bandwidth, it was still being multiplied by the data covariance (as is needed for Scott and Silverman rules).  If scalar value(s) are provided do not rescale by covariance.
      - `cdf()`  [NEW-METHOD]
        - Calculate the CDF by integrating the KDE-derived CDF.  This could be done much better.
        - Seems to be working based on simple tests in 1D and 2D.
  - `plot.py` [NEW-FILE]
    - Plotting related functionality; not imported by default - primarily for internal usage.
    - `align_axes_loc()`  [NEW-METHOD]
      - Align a twin axes to a particular location of the base axes.
    - `draw_carpet_fuzz()`  [NEW-METHOD]
      - Draw a fuzz-style carpet plot
    - `nbshow()`  [moved from `utils.py`]
    - `save_fig()`  [moved from `utils.py`]
    - `smap()`  [NEW-METHOD]
      - Construct a ScalarMappable object (with colormap and normalization) for plotting.
    - `Plot_Control`  [moved from `utils.py`]
  - `utils.py`
    - Moved plotted related methods to `plot.py`
    - `assert_true()`  [NEW-METHOD]
      - Internal testing method.
    - `bins()`
      - Added some docstrings
    - `cumsum()` [NEW-METHOD]
      - Calculate cumulative sums along either a single axis, or all axes (unlike `numpy.cumsum`)
    - `cumtrapz()`
      - Added docstrings
    - `really1d()`  [NEW-METHOD]
      - Check if the given array is really one-dimensional (as opposed to a jagged array)
    - `run_if()`
      - Add `otherwise` argument for functions to run when negation
      - Applies to all `run_if_*` methods.
    - `spacing()`
      - BUG: convert `num` to integer before usage.
  - `tests/`
    - `test_utils.py`
      - Added tests for `cumsum()`
- `notebooks/`
  - Update and use the `init.ipy` for the initialization cell of each notebook.  Default save plots/files to notebooks/output


## v0.2.4 - 2020/03/25
- `Triweight` kernel temporarily disabled as it's having normalization problems in ND > 1.

- `kalepy/`
    - `kde_base.py`
        - `class KDE`
            - Addition (uncaught) keyword-arguments are passed from `KDE` initialization to `Kernel` initialization, so that additional arguments (e.g. `chunk`) can be passed along.
    - `kernels.py`
        - BUG: `Triweight` kernel is not working --> disabled kernel.
        - `class Kernel`
            - Implemented 'chunking' for resampling calculation.  Currently only reflection.
                - This produces an *extreme* memory and time performance increase.  For certain parameters, empirically a chunk size of ~ 1e5 seems to work best.
            - `resample()`
                - BUG: non-integer values of `size` would result in an error.
        - `class Distribution`
            - Significant improvements to the way CDFs are handled.
            - `ppf()`  [new-function]
                - "Percent point function" the inverse of the CDF (returns quantiles given cumulative-probabilities).
    - `utils.py`
        - `bound_indices()`
            - BUG: error in boolean logic.
        - `check_path()`  [new-function]
            - Create the given path if it does not already exist.
        - `cumtrapz()`  [new-function]
            - Cumulative summation using the trapezoid-rule.  Light wrapper around  the `trapz_dens_to_mass()` function.
        - `modify_exists()`  [new-function]
            - Modify the given filename if it already exists.
        - `run_if()`  [new-function]
            - New functions for running passed methods if the current environment is the target environment.
        - `save_fig()`  [new-function]
            - Save a `matplotlib` figure adding convenience features.
- `docs/`
    - `logo/`
        - Logo associated data files.
- `notebooks/`
    - `performance.ipynb`  [new-file]
        - New notebook for performance checks, comparisons and diagnostics.



## v0.2.3 - 2019/06/17
- Added code producing a `kalepy` logo, which is added to the attached media and README file.
- Updated notebooks to fix a few minor errors.



## v0.2.2 - 2019/06/11
- Significant improvement in memory and speed while resampling with reflecting boundaries by implementing chunking.



## v0.2.1 - 2019/06/09
- `kalepy/`
    - `__init__.py`
        - Import desired API methods into module namespace.  Use `__all__` in both `kernels.py` and `utils.py`.
    - `kde_base.py`
        - `class KDE`
            - Introduce `helper` argument upon initialization which determines if extra checks and verbose feedback are given.
            - Introcuce `bw_rescale` initialization argument to rescale the bw-matrix by some factor (matrix, or array).
            - `pdf_grid()`  [new-function]
                - Convenience / wrapper function to calculate the PDF given the edges of a grid.
    - `kernels.py`
        - Introduce `helper` parameter, see `class KDE`
        - Allow the `keep` parameter to be `True` in which case all parameters are kept, or `False` and none are kept (same as `None`).
        - `_check_reflect()`
            - Add additional checks for where the reflection boundaries are relative to the data-values and bandwidth.
        - `_resample_reflect()`
            - BUG: reflection was actually a periodic boundary (ish), instead of reflection.  Not sure why it was still behaving well in testing...
            - BUG: reflection was unnecessarily duplicating (already reflected) data, making fewer new points valid.
    - `utils.py`
        - `ave_std()`  [new-function]
            - Calculation of (optionally) *weighted* average and standard-deviation.
        - `bound_indices()`
            - Allow boundaries to be `None` (for no boundaries)
        - `percentiles()`  [new-function]
            - Copied from `zcode.math.statistic`, allows for weighted percentiles.
        - `stats_str()`
            - Copied function from `zcode.math.math_core` with more extended functionality.
        - `trapz_dens_to_mass()`
            - New argument `axis` to integrate only along target axes.
        - `trapz_nd()`
            - New argument `axis` to integrate only along target axes.
- `notebooks/`
    - `init.ipy`     [new-file]
        - Convenience script for setting up the imports in each notebook file
    - `utils.ipynb`  [new-file]
        - New notebook for testing/exploring the `utils.py` submodule.



## v0.2 – 2019/06/03
- Module renamed from `kdes` to `kalepy`.
- Notebooks are now included in travis unit testing.
- Added skeleton for sphinx documentation; not written yet.

- `README.md`
    - Added installation information and basic examples.
- `kalepy/`
    - `bandwidths.py`
    - `kde_base.py`  [new-file]
        - `class KDE`  [new-class]
            - Primary API for using the `kalepy` package.  Uses passed data and options to construct KDEs by interfacing with `Kernel` instances.
            - The `KDE` class calculates the bandwidth and constructs a `kernel` instance, and handles passing the data and covariance matrix to the kernel as needed.
            - `pdf()`
                - Interface to the kernel instance method: `kernel.pdf()`
            - `resample()`
                - Interface to the kernel instance method: `kernel.resample()`
    - `kernels.py`  [new-file]
        - Stores classes and methods for handling the kernels and their underlying distribution functions.
        - NOTE: some of the scaling and normalization does not work properly in multi-dimensions for all kernels.
        - `class Kernel`
            - Stores a covariance-matrix and uses it as needed with a `Distribution` class instance.
        - `class Distribution`
            - Subclassed to implement particular distribution functions to use in a kernel.
            - Agnostic of the data and covariance.  The `Kernel` class handles the covariance matrix and appropriately transforming the data.
        - `class Gaussian(Distribution)`
            - Gaussian/Normal distribution function with infinite support.
        - `class Box_Asym(Distribution)`
            - Boxcar/rectangle/uniform function with finite support.
        - `class Parabola(Distribution)`
            - Epanechnikov kernel-function with finite support.
        - `class Triweight`
            - Cubic kernel, similar to Parabola but with additional smooth derivatives.
            - WARNING: does not currently work in multiple-dimensions (normalization is off).
        - `get_all_distribution_classes()`
            - Method to retrieve a list of all `Distribution` sub-classes.  Mostly used for testing.
        - `get_distribution_class()`
            - Convert from the argument to a `Distribution` subclass as needed.  This argument can convert from a string specification of a distribution function to return the actual class.
    - `utils.py`
        - `class Test_Base`
            - Base-class to use in unittests.
        - `add_cov()`
            - Given a covariance matrix, use a Cholesky decomposition to transform the given data to have that covariance.
        - `allclose()`   [new-function]
            - Convenience function for unittests.
        - `alltrue()`    [new-function]
            - Convenience function for unittests.
        - `array_str()`  [new-function]
            - Format an array (or elements of) for printing.
        - `bins()`       [new-function]
            - Generate bin- edges, centers and widths all together.
        - `bound_indices()`
            - Find the indices of parameter space arrays within given bounds.
        - `cov_from_var_cor()`
            - Construct a covariance matrix given a set of variances of parameters, and the correlations between them.
        - `matrix_invert()`
            - Invert a matrix, following back to SVD if it initially fails.
        - `rem_cov()`
            - Given a covariance matrix, use a Cholesky decomposition to remove that covariance from the given data.
        - `stats_str()`  [new-function]
            - Method for calculating percentiles of given data and returning them as a str.
        - `trapz_dens_to_mass()`
            - Use the ndimensional trapezoid rule to convert from densities on a grid to masses (e.g. PDF to PMF).
    - `tests/`
        - `test_distributions.py`
            - Test the underlying distribution functions.
        - `test_kde.py`
            - Test the top-level KDE class and the accuracy of KDE calculation of PDFs and resampling.
        - `test_kernels.py` [new-file]
            - Tests of the kernels directly.
        - `test_utils.py`
            - Test the utility functions.

- `notebooks/`
    - `kernels.ipynb`  [new-file]
        - Examining / testing the behavior of different kernels specifically.
    - `demo.ipynb`     [new-file]
        - Currently includes the material used in the `README.rst`, should be expanded as a quick demonstration / tutorial of the package.



## v0.1 – 2019/05/19
- `kdes/`
    - `__init__.py`
        - `class KDE`
            - Base class for KDE calculations, modeled roughly on the `scipy.stats.gaussian_kde` class.
            - Allows for multidimensional PDF calculation and resampling of data, in multi-dimensional parameter spaces.
            - Reflecting boundary conditions are available in multiple dimensions, both for PDF calculation and resampling.
    - `utils.py`
        - General utility functions for the package.  Methods extracted from the `zcode` package.
        - `midpoints()`
            - Calculate the midpoints between values in an array, either in log or linear space.
        - `minmax()`
            - Calculate the extrema of a given dataset.  Allows for comparison with previous extrema, setting limits, or 'stretching' the return values by a given amount.
        - `spacing()`
            - Construct a linear or log spacing between the given extrema.
    - `tests/`
        - `test_kde.py`
            - Basic tests for the `KDE` base class and its operations.
        - `test_util.py`
            - Basic tests for the utility methods.

- `notebooks/`
    - `kde.ipynb`
        - Includes basic examples and tests with plots.  Mostly the same tests as in the `kdes/tests/` directory, but with plots.
