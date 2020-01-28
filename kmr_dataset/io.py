import os
import numpy as np
from collections import defaultdict
from glob import glob
from scipy.sparse import csr_matrix
from .install import _check_install


installpath = os.path.abspath(os.path.dirname(__file__))

def _check_size(size, force=False):
    if force:
        return True
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


def get_paths(directory=None, size='small', force=False):
    """
    Arguments
    ---------
    directory : str or None
        Data stored directory path
    size : str
        Choose one of ['small', '2m', '5m']
        Or you can set ``force`` as True if you have same formed dataset
    force : Boolean
        If you have same fomed dataset, set ``directory`` and ``force=True``

    Returns
    -------
    paths : list of str
        List of file path which are availble to load

    Usage
    -----
        >>> from kmr_dataset import get_paths
        >>> paths = get_paths(size='2m')

        >>> import pandas as pd
        >>> movies = pd.read_csv(paths[3], delimiter='\t')
    """
    _check_size(size, force)
    directory = _initialize_dir(directory, size)
    if size == 'small':
        paths = _get_paths_small(directory)
    else:
        paths = _get_paths_large(directory, size)

    _check_install(paths, size)
    return paths

def _prepare_rate_loader(directory, size):
    _check_size(size)

    directory = _initialize_dir(directory, size)
    if size == 'small':
        path = f'{directory}/rates.csv'
    else:
        path = f'{directory}/rates-{size}.csv'

    _check_install([path], size)

    def parser(line):
        return [int(col) for col in line.strip().split(',')]

    return path, parser

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

    path, parser = _prepare_rate_loader(directory, size)

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

def load_histories(directory=None, size='small'):
    """
    Arguments
    ---------
    directory : str or None
        Data directory. If None, use default directory
    size : str
        Dataset size, Choice one of ['small']

    Returns
    -------
    user_item_history : dict of list

        {
            user: [(item, rate, time), (item, rate, time), ...],
            user: [(item, rate, time), (item, rate, time), ...],
            ...
        }

        time is UNIX time format

    Usage
    -----
        >>> from kmr_dataset import load_history
        >>> histories = load_history(size='small')
    """

    path, parser = _prepare_rate_loader(directory, size)

    histories = defaultdict(lambda: [])
    with open(path, encoding='utf-8') as f:
        # skip head: user,movie,rate,time
        next(f)
        for line in f:
            # user, movie, rate, time
            u, m, r, t = parser(line)
            histories[u].append((m, r, t))
    return dict(histories)
