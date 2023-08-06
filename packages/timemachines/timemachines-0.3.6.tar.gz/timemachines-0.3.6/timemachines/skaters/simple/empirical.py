from timemachines.skatertools.utilities.conventions import Y_TYPE, A_TYPE, R_TYPE, E_TYPE, T_TYPE, wrap
from typing import Any
from timemachines.skatertools.components.parade import parade
from timemachines.skatertools.utilities.nonemath import nonecast

# Fast elementary time series skaters, useful as benchmarks, pre-processing, sub-components etc
# They maintain running mean/std of their own empirical errors


def empirical_last_value(y :Y_TYPE, s:dict, k:int =1, a:A_TYPE =None, t:T_TYPE =None, e:E_TYPE =None)->([float] , Any , Any):
    """ Last value cache, with empirical std """

    if not s.get('p'):
        s = {'p':{}}   # Initialize prediction parade

    if y is None:
        return None, None, s
    else:
        y0 = wrap(y)[0]       # Ignore the rest
        x = [y0]*k            # What a great prediction !
        bias, x_std, s['p'] = parade(p=s['p'], x=x, y=y0)  # update residual queue
        return x, x_std, s


def empirical_ema_r1(y :Y_TYPE, s, k:int, a:A_TYPE =None, t:T_TYPE =None, e:E_TYPE =None, r:R_TYPE=None):
    """ Exponential moving average, with empirical std

          r      weight to place on existing anchor point

    """
    assert r is not None
    y0 = wrap(y)[0]
    if not s.get('p'):
        s = {'p':{},
             'x':y0,
             'rho':r}
        assert 0 <= s['rho'] <= 1, 'Expecting rho=r to be between 0 and 1'
    else:
        assert abs(r-s['rho'])<1e-6,'rho=r is immutable'

    if y0 is None:
        return None, s, None
    else:
        s['x'] = s['rho']*s['x'] + (1-s['rho'])*y0         # Make me better !
        x = [s['x']]*k
        _we_ignore_bias, x_std, s['p'] = parade(p=s['p'], x=x, y=y0)
        x_std_fallback = nonecast(x_std,fill_value=1.0)
        return [s['x']] * k, x_std_fallback, s


def slowly_moving_average(y :Y_TYPE, s, k:int, a:A_TYPE =None, t:T_TYPE =None, e:E_TYPE =None):
    return empirical_ema_r1(y=y, s=s, k=k, a=a, t=t, e=e, r=0.95)


def quickly_moving_average(y :Y_TYPE, s, k:int, a:A_TYPE =None, t:T_TYPE =None, e:E_TYPE =None):
    return empirical_ema_r1(y=y, s=s, k=k, a=a, t=t, e=e, r=0.75)




BASIC_SKATERS = [empirical_last_value, slowly_moving_average, quickly_moving_average]
BASIC_R1_SKATERS = [empirical_ema_r1]


if __name__=='__main__':
    from timemachines.skatertools.data.real import hospital_with_exog
    from timemachines.skatertools.evaluation.evaluators import evaluate_mean_absolute_error

    k = 3
    y, a = hospital_with_exog(k=k,n=500)
    f = empirical_ema_r1
    err1 = evaluate_mean_absolute_error(f=f, k=k, y=y, a=a, r=0.9, n_burn=50)













