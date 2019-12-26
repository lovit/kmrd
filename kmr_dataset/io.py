import os
import numpy as np
from glob import glob
from scipy.sparse import csr_matrix
from .install import _check_install


installpath = os.path.abspath(os.path.dirname(__file__))

def _initialize_dir(directory, size):
    if directory is None:
        return f'{installpath}/datafile/kmrd-{size}/'
    return f'{directory}/'

def get_paths(directory=None, size='small'):
    directory = _initialize_dir(directory, size)
    paths = glob(f'{directory}/*.txt') + glob(f'{directory}/*.csv')
    paths = sorted(paths)
    return paths

def load_rates(directory=None, size='small'):
    """
    Arguments
    ---------
    directory : str or None
        Data directory. If None, use default directory
    size : str
        Dataset size, Choice one of ['small']

    Returns
    -------
    rates : scipy.sparse.csr_matrix
        (user, movie) = rate
    timestamps : numpy.ndarray
        UNIX time, corresponding rates.data

    Usage
    -----
        >>> from kmr_dataset import load_rates
        >>> rates, timestamps = load_rates(size='small')
    """
    path = _initialize_dir(directory, size) + 'rates.csv'
    _check_install(path)

    def parser(line):
        return [int(col) for col in line.strip().split(',')]

    rows, cols, data, timestamps = [], [], [], []
    exists = set()

    n_continues = 0
    with open(path, encoding='utf-8') as f:
        # skip head: user,movie,rate,time
        next(f)
        for line in f:
            i, j, v, t = parser(line)
            key = (i,j)
            if key in exists:
                n_continues += 1
                continue
            rows.append(i)
            cols.append(j)
            data.append(v)
            timestamps.append(t)
            exists.add(key)

    if n_continues > 0:
        flag = len(rows) == len(cols) == len(data) == len(timestamps)
        if flag:
            print(f'skip {n_continues} lines, #uniques={len(rows)}')
        else:
            raise ValueError(f'There unexpected error in data {path}')

    rates = csr_matrix((data, (rows, cols)))
    timestamps = np.array(timestamps, dtype=np.int)
    return rates, timestamps
