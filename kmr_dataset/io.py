import os
import numpy as np
from glob import glob
from scipy.sparse import csr_matrix
from .install import _check_install


installpath = os.path.abspath(os.path.dirname(__file__))

def _check_size(size):
    available_size = '2m 5m small'.split()
    if not (size in available_size):
        raise ValueError(f'Size must be one of {available_size}')

def _initialize_dir(directory, size):
    if directory is not None:
        directory = f'{directory}/datafile/'
        if not os.path.exists(directory):
            raise ValueError(f'Directory {directory} must include "datafile/kmrd-small/" and "datafile/kmrd/"')
    else:
        directory = f'{installpath}/datafile/'

    if size == 'small':
        return f'{directory}/kmrd-small/'
    return f'{directory}/kmrd/'

def _get_paths_small(directory):
    files = 'castings.csv countries.csv genres.csv movies.txt peoples.txt rates.csv'.split()
    paths = [f'{directory}/{file}' for file in files]
    return paths

def _get_paths_large(directory, size):
    files = 'castings.csv countries.csv genres.csv movies.txt peoples.txt rates.csv'.split()
    files[-1] = f'rates-{size}.csv'
    paths = [f'{directory}/{file}' for file in files]
    return paths

def get_paths(directory=None, size='small'):
    _check_size(size)
    directory = _initialize_dir(directory, size)
    if size == 'small':
        paths = _get_paths_small(directory)
    else:
        paths = _get_paths_large(directory, size)

    _check_install(paths, size)
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

    _check_size(size)

    directory = _initialize_dir(directory, size)
    if size == 'small':
        path = f'{directory}/rates.csv'
    else:
        path = f'{directory}/rates-{size}.csv'

    _check_install([path], size)

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
