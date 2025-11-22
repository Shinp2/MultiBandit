#!/usr/bin/env python3
"""Small helper module to compute confidence-interval half-widths.

Provides ci_halfwidth(vals, conf=0.95) which returns the half-width in the
same units as the observations. Uses scipy.stats.t if available, otherwise
falls back to z=1.96 as an approximation for the critical value.
"""
import math
import statistics
try:
    from scipy import stats
    _HAVE_SCIPY = True
except Exception:
    _HAVE_SCIPY = False


def ci_halfwidth(vals, conf=0.95):
    """Return half-width of the (conf) confidence interval for the mean of vals.

    vals: sequence of numeric observations (length n)
    conf: confidence level (e.g. 0.95)

    Returns 0.0 for n <= 1 (no interval can be computed).
    """
    n = len(vals)
    if n <= 1:
        return 0.0
    s = statistics.stdev(vals)
    se = s / math.sqrt(n)
    alpha = 1.0 - conf
    if _HAVE_SCIPY:
        tcrit = stats.t.ppf(1.0 - alpha/2.0, df=n-1)
    else:
        tcrit = 1.96
    return tcrit * se
