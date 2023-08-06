try:
    import pyflux as pf
except ImportError:
    class Mock:
        ARIMA = None
    pf = Mock()
    print('pyflux is off the list while the package on PyPI is broken. You can install from git')
    print('pip install git+https://github.com/RJT1990/pyflux.git')

import pandas as pd
from timemachines.skatertools.visualization.priorplot import prior_plot_exogenous
from timemachines.skatertools.utilities.conventions import to_int_log_space, initialize_buffers, split_exogenous, update_buffers, \
    R_TYPE

# TODO: Span models at https://pyflux.readthedocs.io/en/latest/gpnar.html with r


def flux_hyperparams(s, r: R_TYPE):
    # Interpret hyper-parameters - r is only used once at initiation of model
    integ_bounds, ar_bounds, ma_bounds =(0,2), (0.55, 2.45), (0.66, 10.33)
    s['n_burn'] = 25
    s['alpha'] = 0.25  # Defines confidence interval
    s['buffer_len'] = 5000
    s['integ'], s['ar'], s['ma'] = to_int_log_space(r, bounds=[integ_bounds, ar_bounds, ma_bounds])
    s['family'] = pf.Normal()
    return s


def flux_or_last_value(s, k:int, exog:[float], y0:float):
    # We fit each time
    if s.get('model') is None:
        return y0, s, None
    else:
        y_hat = s['model'].predict(h=k)
        x = y_hat.values[0][0]
        w = None
        return x, s, w


def flux_auto(y, s, k, a, t, e, r):
    """ One way to use flux package

            - Contemporaneous y[1:] variables are used as exogenous 'X' in pmdarima
            - This only works for k=1

        :returns: x, s', w
    """
    if s is None:
        s = dict()
        s = flux_hyperparams(s=s,r=r)
        s = initialize_buffers(s=s,y=y)

    if y is not None:
        # Process observation and return prediction
        assert isinstance(y, float) or len(y) == s['dim'], ' Cannot change dimension of input in flight '
        y0, exog = split_exogenous(y=y, dim=s['dim'])
        s = update_buffers(s=s, a=a, exog=exog, y0=y0)
        if True:  # Always fit prior to prediction
            none_, s, _ = flux_auto(y=None, s=s, k=k, a=a, t=t, e=e, r=r)  # Fit the model
            assert none_ is None
        return flux_or_last_value(s=s,k=k,exog=exog,y0=y0)

    if y is None:
        if len(s.get('buffer'))<s['n_burn']:
            s['model'] = None
        else:
            data = pd.DataFrame(columns=['y'], data=s.get('buffer'))
            s['model'] = pf.ARIMA(data=data, ar=s['ar'], ma=s['ma'], target='y', family=s['family'])
            _ = s['model'].fit("MLE")
        return None, s, None  # Acknowledge that a fit was requested by returning x=None, w=None


if __name__ == '__main__':
    err = prior_plot_exogenous(f=flux_auto, k=1, n=200, r=0.05)
    pass
