import argparse
import os
from glob import glob
from maker import make_casting, make_directing, make_meta
from maker import make_rates


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str, default='../scraped/', help='Raw data directory')
    parser.add_argument('--dataset_dir', type=str, default='../dataset/', help='Dataset directory')
    parser.add_argument('--min_count', type=int, default=20, help='User min count')
    parser.add_argument('--volume_unit', type=int, default=1000000, help='Volume unit')
    parser.add_argument('--debug', dest='debug', action='store_true')

    args = parser.parse_args()
    data_dir = args.data_dir
    dataset_dir = args.dataset_dir
    min_count = args.min_count
    volume = args.volume_unit
    debug = args.debug

    if not os.path.exists(dataset_dir):
        os.makedirs(dataset_dir)

    movie_indices = [int(path.split('/')[-1][:-5]) for path in glob(f'{data_dir}/meta/*')]
    movie_indices += [int(path.split('/')[-1]) for path in glob(f'{data_dir}/comments/*')]
    movie_indices = sorted(set(movie_indices))
    print(f'Found {len(movie_indices)} movies')

    if debug:
        movie_indices = sorted(
            [10107, 134963, 89755, 129049, 129050, 121922,
             39516, 137952, 69023, 52747, 24452, 13252]
        )

    #make_meta(data_dir, movie_indices, dataset_dir)
    #make_directing(data_dir, movie_indices, dataset_dir)
    #make_casting(data_dir, movie_indices, dataset_dir)
    make_rates(data_dir, debug, min_count, dataset_dir, volume)

if __name__ == '__main__':
    main()
