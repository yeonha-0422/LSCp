from numba import njit
import numpy as np
from scipy.special import betainc


# from scipy.stats import pearsonr

def pearsonr(x, y):
    """ Calculate Pearson Correlation between x and y
    :param x:
    :param y:
    :return:
    """
    x = np.asarray(x)
    y = np.asarray(y)

    # if np.unique(x).shape[0] == 1 or np.unique(y).shape[0] == 1:
    #     return 1.0
    r = pearsonr_helper(x, y)

    #    Presumably, if abs(r) > 1, then it is only some small artifact of
    #    floating point arithmetic.
    r = max(min(r, 1.0), -1.0)
    return r


@njit
def pearsonr_helper(x, y):
    """ Optimized version for Pearson correlation calculation
    :param x:
    :param y:
    :return:
    """
    # x and y should have same length.
    #    n = len(x)
    mx = x.mean()
    my = y.mean()
    xm, ym = x - mx, y - my
    # r_num = np.add.reduce(xm * ym)

    r_num = np.sum(xm * ym)
    r_den = np.sqrt(np.sum(xm * xm, axis=0) * np.sum(ym * ym, axis=0))

    # only use in case of overflow
    # if r_den == 0:
    #     return 1
    r = r_num / r_den

    return r


def wpearsonr(x, y, w=None):
    """ Weighted Pearson Correlation
    :param x:
    :param y:
    :param w:
    :return:
    """
    # https://stats.stackexchange.com/questions/221246/such-thing-as-a-weighted-correlation

    # unweighted version
    if w is None:
        return pearsonr(x, y)

    x = np.asarray(x)
    y = np.asarray(y)
    w = np.asarray(w)

    n = len(x)

    w_sum = w.sum()
    mx = np.sum(x * w) / w_sum
    my = np.sum(y * w) / w_sum

    xm, ym = (x - mx), (y - my)

    r_num = np.sum(xm * ym * w) / w_sum

    xm2 = np.sum(xm * xm * w) / w_sum
    ym2 = np.sum(ym * ym * w) / w_sum

    r_den = np.sqrt(xm2 * ym2)
    r = r_num / r_den

    r = max(min(r, 1.0), -1.0)
    #    df = n - 2
    #
    #    if abs(r) == 1.0:
    #        prob = 0.0
    #    else:
    #        t_squared = r ** 2 * (df / ((1.0 - r) * (1.0 + r)))
    #        prob = _betai(0.5 * df, 0.5, df / (df + t_squared))
    return r  # , prob


#####################################
#      PROBABILITY CALCULATIONS     #
#####################################


def _betai(a, b, x):
    x = np.asarray(x)
    x = np.where(x < 1.0, x, 1.0)  # if x > 1 then return 1.0
    return betainc(a, b, x)


def pearsonr_mat(mat, w=None):
    n_row = mat.shape[0]
    n_col = mat.shape[1]
    pear_mat = np.full([n_row, n_row], 1).astype(float)

    if w is not None:
        for cx in range(n_row):
            for cy in range(cx + 1, n_row):
                curr_pear = wpearsonr(mat[cx, :], mat[cy, :], w)
                pear_mat[cx, cy] = curr_pear
                pear_mat[cy, cx] = curr_pear
    else:
        for cx in range(n_col):
            for cy in range(cx + 1, n_row):
                curr_pear = pearsonr(mat[cx, :], mat[cy, :])[0]
                pear_mat[cx, cy] = curr_pear
                pear_mat[cy, cx] = curr_pear

    return pear_mat
