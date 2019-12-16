import os
import numpy as np
from scipy.sparse import csr_matrix


installpath = os.path.abspath(os.path.dirname(__file__))

def _initialize_dir(directory, size):
    if directory is None:
        directory = installpath
    return f'{directory}/datafile/kmrd-small/'

def _check_install(path):
    if not os.path.exists(path):
        raise ValueError(f"Datfiles has not been installed yet\npath = {path}")

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
    timestamp : numpy.ndarray
        UNIX time, corresponding rates.data
    """
    path = _initialize_dir(directory, size) + 'rates.csv'
    _check_install(path)

    def parser(line):
        return [int(col) for col in line.strip().split(',')]

    rows, cols, data, timestamp = [], [], [], []

    with open(path, encoding='utf-8') as f:
        # skip head: user,movie,rate,time
        next(f)
        for line in f:
            i, j, v, t = parser(line)
            rows.append(i)
            cols.append(j)
            data.append(v)
            timestamp.append(t)

    rates = csr_matrix((data, (rows, cols)))
    timestamp = np.array(timestamp, dtype=np.int)
    return rates, timestamp
