import warnings
import numpy as np
from scipy.optimize import least_squares

DES_FILTERS = 'griz'


class FeatureExtractor():
    def __init__(self):
        pass

    def fit(self, X_df, y):
        pass

    # def transform(self, X_df, snr_cut=1, nepoch_cut=5):
    #     X_df = filter_snr(X_df, snr_cut, nepoch_cut)
    #     return parametric_fit(X_df)

    def transform(self, X_df):
        return parametric_fit(X_df)


def filter_snr(X_df, min_snr, min_epoch):
    """
    Perform a cut on the data with respect to the SNR of each point

    Parameters
    ----------
    X_df : DataFrame
        data frame of SN lightcurves
    min_snr : int or float
        SNR value under which data point should be discarded
    min_epoch : int or float
        min number of values per lightcurve to consider a fit

    Returns
    -------
    thresholded data frame

    """
    meta_cut = np.ones(len(X_df), dtype=bool)
    # For each light curve
    for filt in DES_FILTERS:
        # Compute the SNR (flux / flux_err)
        serie = X_df['%s_fluxcal' % filt] / X_df['%s_fluxcalerr' % filt]
        # Threshold it
        serie = serie.apply(lambda x: x > min_snr)
        # Discard if not enough remaining values
        serie = serie.apply(lambda x: np.sum(x) > min_epoch)
        # Add to the total cut
        meta_cut = np.logical_and(meta_cut, serie.values)

    return X_df[meta_cut]


def _bazin(time, A, B, t0, tfall, trise):
    """
    Parametric light curve function proposed by Bazin et al., 2009.

    Parameters
    ----------
    time : array_like
        exploratory variable (time of observation)
    A, B, t0, tfall, trise : float
        curve parameters

    Returns
    -------
    array_like
        response variable (flux)

    """
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', category=RuntimeWarning)
        X = np.exp(-(time - t0) / tfall) / (1 + np.exp((time - t0) / trise))

    return A * X + B


def _fit_lightcurve(time, flux):
    """
    Find best-fit parameters using scipy.least_squares.

    Parameters
    ----------
    time : array_like
        exploratory variable (time of observation)
    flux : array_like
        response variable (measured flux)

    Returns
    -------
    output : list of float
        best fit parameter values

    """
    scaled_time = time - time.min()
    t0 = scaled_time[flux.argmax()]
    guess = (0, 0, t0, 40, -5)

    def errfunc(params, time, flux):
        return abs(flux - _bazin(time, *params))

    result = least_squares(errfunc, guess,
                           args=(scaled_time, flux),
                           method='lm')

    return result.x


def parametric_fit(X_df, filters=DES_FILTERS):
    """
    Perform a fit on every light curve and return the fit parameters

    Parameters
    ----------
    X_df : DataFrame
        data frame of SN lightcurves

    Returns
    -------
    data frame of the parameters of the fit for each filter

    """
    n_params = 5
    full_params = np.zeros((len(X_df), len(filters) * n_params))
    for idx, snid in enumerate(X_df.index):
        params = np.zeros((len(filters), n_params))
        for id_filt, filt in enumerate(filters):
            time = X_df.loc[snid, '%s_mjd' % filt]
            flux = X_df.loc[snid, '%s_fluxcal' % filt]
            try:
                params[id_filt] = _fit_lightcurve(time, flux)
            except ValueError:
                continue
        full_params[idx] = params.ravel()

    return full_params
