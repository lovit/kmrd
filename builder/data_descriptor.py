import numpy as np
from bokeh.palettes import Blues
from bokeh.plotting import figure


def plot_user_rates(x, min_counts, noise_levels, data_name):
    """
    Usage
    -----
        >>> min_counts = [2, 5, 20, 50]
        >>> noise_levels = [0.0, 0.005, 0.01, 0.02, 0.03, 0.05]
        >>> figures = plot_user_rates(kmr, min_counts, noise_levels, 'KMRD-13')

        >>> min_counts = [25, 100, 200, 500]
        >>> noise_levels = [0.0, 0.005, 0.01, 0.02]
        >>> figures = plot_user_rates(ml, min_counts, noise_levels, 'MovieLens-20m')
    """
    sorted_indices, sorted_indices_nz, bincount = sort_by_frequency(x.nonzero()[0])
    sorted_bincount = bincount[sorted_indices_nz]
    line_x_indices = np.asarray([np.where(bincount >= mc)[0].shape[0]-1 for mc in min_counts])
    texts = [f'# >= {mc}' for mc in min_counts]
    cum = np.cumsum(sorted_bincount) / sorted_bincount.sum()

    noise_indices = [np.where(cum <= lv)[0].shape[0] for lv in noise_levels]
    titles = []
    for lv, idx in zip(noise_levels, noise_indices):
        covered = 100 * sorted_bincount[idx:].sum() / sorted_bincount.sum()
        titles.append(f'{data_name} >= {lv:.2} (-{idx} idxs)')

    figures = plot_cumulations(cum, line_x_indices, texts, noise_indices, titles)
    return figures

def sort_by_frequency(indices):
    bincount = np.bincount(indices, minlength=indices.max())
    num_nonzero = np.unique(indices).shape[0]
    sorted_indices = bincount.argsort()[::-1]
    nonzero_sorted_indices = sorted_indices[:num_nonzero]
    return sorted_indices, nonzero_sorted_indices, bincount

def plot_cumulations(cum, line_x_indices, texts, noise_x_indices, titles):
    figures = []
    for begin, title in zip(noise_x_indices, titles):
        cum_ = cum.copy()[begin:]
        cum_ = (cum_ - cum_[0]) / (cum_[-1] - cum_[0])
        line_x_indices_ = line_x_indices - begin
        p = plot_cumulation(cum_, line_x_indices_, texts, title)
        figures.append(p)
    return figures

def plot_cumulation(cum, line_x_indices, texts, title):
    log_max = np.log(cum.shape[0]+1)
    x_samples = np.linspace(0, log_max, int(log_max*20))
    sample_indices = np.array(np.exp(x_samples) - 1, dtype=np.int)
    sample_indices = sample_indices[np.where(sample_indices < cum.shape[0])[0]]
    x_samples = x_samples[:sample_indices.shape[0]]
    cum_samples = cum[sample_indices]
    p = figure(height=300, width=600, x_range=(0, log_max), y_range=(0, 1.1), title=title,
               x_axis_label = 'log (unique users)', y_axis_label = '% of rates')
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.line(x_samples, cum_samples)
    for x, text, color in zip(line_x_indices, texts, Blues[9]):
        y = cum[x]
        log_x = np.log(x)
        p.line([log_x, log_x, 0], [0, y, y], line_dash=(3,3), line_color='grey')
        percent = 100 * x / cum.shape[0]
        p.text(0.5, y, text=[f'{100*y:.3}% rates, {x} users ({percent:.3}%, {text})'],
           text_color=color, text_align="left", text_font_size="10pt")
    x = np.where(cum <= 0.1)[0].shape[0]
    y = cum[x]
    log_x = np.log(x)
    p.line([log_x, log_x, 0], [0, y, y], line_dash=(3,3), line_color='grey')
    p.text(0.5, y, text=[f'10% rates, top {x} / {cum.shape[0]} usres'],
       text_color="firebrick", text_align="left", text_font_size="10pt")
    return p

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
