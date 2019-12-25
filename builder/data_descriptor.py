import numpy as np


def describe_stats(x, row_name='user', col_name='item', data_name=''):
    """
    Arguments
    ---------
    x : scipy.sparse.csr_matrix
        Rates matrix
    row_name : str
        Row name which used in print message
    col_name : str
        Column name which used in print message
    data_name : str
        Data name which used in print message

    Usage
    -----
        >>> describe(ml, data_name='MovieLens-20m')
        $ Description of MovieLens-20m
           - num user : 138494
           - num item : 131263
           - num unique user : 138493 (100.0 %)
           - num unique item : 26744 (20.37 %)
           - num of nonzero : 20000263
           - sparsity : 0.9988998233532408
           - sparsity (compatified) : 0.9946001521864456

        >>> describe(kmr, data_name='KMRD-12m')
        $ Description of KMRD-12m
           - num user : 2819051
           - num item : 190980
           - num unique user : 2819051 (100.0 %)
           - num unique item : 19227 (10.07 %)
           - num of nonzero : 12167619
           - sparsity : 0.9999773996700032
           - sparsity (compatified) : 0.9997755130273684
    """
    n_rows, n_cols = x.shape
    rows, cols = x.nonzero()
    nnz = rows.shape[0]
    sparsity = 1 - nnz / ((rows.max() + 1) * (cols.max() + 1))
    unique_rows = np.unique(rows)
    unique_cols = np.unique(cols)
    n_unique_rows = unique_rows.shape[0]
    n_unique_cols = unique_cols.shape[0]
    sparsity_unique = 1 - nnz / (n_unique_rows * n_unique_cols)

    dataname_ = 'of ' + data_name if data_name else ''
    print(f"""Description {dataname_}
 - num {row_name} : {n_rows}
 - num {col_name} : {n_cols}
 - num unique {row_name} : {n_unique_rows} ({100 * n_unique_rows / n_rows:.4} %)
 - num unique {col_name} : {n_unique_cols} ({100 * n_unique_cols / n_cols:.4} %)
 - num of nonzero : {nnz}
 - sparsity : {sparsity}
 - sparsity (compatified) : {sparsity_unique}
         """)
