import os
import json
import numpy as np
from collections import Counter
from datetime import datetime
from glob import glob
from .utils import initialize_usermapper
from .utils import save_usermapper
from .utils import save_rows
from .utils import load_usermapper
from .utils import load_list_of_dict
from .utils import mask_user
from .utils import to_unix_time

def make_rates(data_dir, debug, min_count, dataset_dir, volume=1000000):
    data_users = load_comments(data_dir, debug)

    ##############################
    # frequency filtered dataset #
    dataname = f'kmrd-{int(len(data_major) / volume)}m'
    user_idxs, movie_idxs, idxs, rates, timestamps, texts = zip(*data_major)

    def save(user_idxs, movie_idxs, idxs, rates, timestamps, texts, users, dataname):
        if not os.path.exists(f'{dataset_dir}/{dataname}'):
            os.makedirs(f'{dataset_dir}/{dataname}')

        rates_dump = tuple(zip(user_idxs, movie_idxs, rates, timestamps))
        rates_path = f'{dataset_dir}/{dataname}/rates.csv'
        save_rows(rates_dump, rates_path, 'user,movie,rate,time', ',')

        texts_dump = tuple(zip(user_idxs, movie_idxs, rates, texts))
        texts_path = f'{dataset_dir}/{dataname}/texts.txt'
        save_rows(texts_dump, texts_path, 'user\tmovie\trate\ttext', '\t')

        userlist_path = f'{dataset_dir}/{dataname}/userlist'
        with open(userlist_path, 'w', encoding='utf-8') as f:
            for user in users:
                f.write(f'{user}\n')

        idxs_path = f'{dataset_dir}/{dataname}/idxs'
        with open(idxs_path, 'w', encoding='utf-8') as f:
            f.write('comment_idx\n')
            for idx in idxs:
                f.write(f'{idx}\n')

    save(user_idxs, movie_idxs, idxs, rates, timestamps, texts, users_major, dataname)
    print('saved filtered dataset')

    ########################
    # non-filtered dataset #
    user_idxs_, movie_idxs_, idxs_, rates_, timestamps_, texts_ = zip(*data_minor)

    # concatenate
    user_idxs += user_idxs_
    movie_idxs += movie_idxs_
    idxs += idxs_
    rates += rates_
    timestamps += timestamps_
    texts += texts_
    users = np.concatenate([users_major, users_minor])
    dataname = f'kmrd-{int(len(rates) / volume)}m'

    save(user_idxs, movie_idxs, idxs, rates, timestamps, texts, users, dataname)
    print('saved non-filtered dataset\ndone')

def load_comments(data_dir, debug):

    def parse_time(yymmdd):
        return int(datetime.strptime(yymmdd, '%y.%m.%d').timestamp())

    paths = glob(f'{data_dir}/user_comments/*/*') + glob(f'{data_dir}/user_comments/*')
    paths = [path for path in paths if os.path.isfile(path)]
    if debug:
        paths = paths[:30]

    data, users = [], []
    duplicated_checker = IndexTable()

    n_exceptions = 0
    n_duplicateds = 0
    n_similars = 0
    user_idx = 0
    n_paths = len(paths)

    for i, path in enumerate(paths):
        if (i > 0) and (i % 1000 == 0):
            percent = 100 * (i+1) / n_paths
            n_data = len(data)
            message = '\rScanning {:.4}%, rates={}, users={}, simialrs={}, duplicated={}, exception={}    '
            message = message.format(percent, n_data, user_idx, n_similars, n_duplicateds, n_exceptions)
            print(message, end='')

        try:
            name = int(path.split('/')[-1])
            comments = load_list_of_dict(path)
        except Exception as e:
            continue

        comments_ = []
        for comment in comments:
            try:
                idx = int(comment['idx'])
                movie_idx = int(comment['movie_idx'])
                rate = int(comment['score'])
                timestamp = parse_time(comment['written_at'])
                text = comment['text']
                comments_.append((idx, movie_idx, rate, timestamp, text))
            except Exception as e:
                n_exceptions += 1

        if len(comments_) == 0:
            continue

        # check duplicated user
        comment_idxs = [idx for idx, _, _, _, _ in comments_]
        primary_key = {(idx, timestamp) for idx, _, _, timestamp, _ in comments_}
#         primary_key = {idx for idx, _, _, timestamp, _ in comments_}
        similar_users = {u for idx in comment_idxs for u in duplicated_checker.comment_to_user.get(idx, [])}

        if similar_users:
            n_similars += 1
            exist = False
            for u in similar_users:
                if primary_key == duplicated_checker.user_to_comments[u]:
                    exist = True
                    break
            if exist:
                n_duplicateds += 1
                continue

        user_idx = len(users)
        users.append(name)
        for idx, movie_idx, rate, timestamp, text in comments_:
            data.append((user_idx, movie_idx, idx, rate, timestamp, text))

        duplicated_checker.insert(user_idx, comment_idxs, primary_key)

        if user_idx < 3:
            print('In duplicated user check')
            print(f'primary key = {primary_key}')
            print(f'comment to user = {duplicated_checker.comment_to_user}\n')

    n_data = len(data)
    suffix = ' ' * 40
    print(f'\rScanning has been finished. Found {n_data} rates{suffix}')
    print(f'Number of exceptions = {n_exceptions}')
    print(f'Number of similar users = {n_similars}, duplicated users = {n_duplicateds}')

    return data, users, duplicated_checker

def split_by_min_count(data, min_count):
    user_size = Counter(row[0] for row in data)
    user_large = {u for u, c in user_size.items() if c >= min_count}
    user_small = {u for u, c in user_size.items() if c < min_count}
    print(f'{len(user_large)} users >= {min_count}, {len(user_small)} users < {min_count}')

    def sort_by_size(userset, user_size):
        return sorted(userset, key=lambda u:-user_size[u])

    user_mapper = {u:idx for idx, u in enumerate(sort_by_size(user_large, user_size))}
    b = len(user_mapper)
    user_mapper.update({u:idx+b for idx, u in enumerate(sort_by_size(user_small, user_size))})

    def transform_idx(row):
        return (user_mapper[row[0]], row[1], row[2], row[3], row[4], row[5])

    data_filtered = [transform_idx(row) for row in data if row[0] in user_large]
    data_full = [transform_idx(row) for row in data]
    userlist_full = [u for u, _ in sorted(user_mapper.items(), key=lambda x:x[1])]
    userlist_filtered = userlist_full[:b]

    data_filtered = sorted(data_filtered)
    data_full = sorted(data_full)

    n_full, n_filtered = len(data_full), len(data_filtered)
    percent = 100 * n_filtered / n_full
    print(f'\nfiltered data size is {percent:.4}% of full data size')
    print(f'#rows of filtered = {n_filtered}, #users = {len(userlist_filtered)}')
    print(f'#rows of full = {n_full}, #users = {len(userlist_full)}')

    return data_filtered, userlist_filtered, data_full, userlist_full


class IndexTable:
    "duplicated user remover"
    def __init__(self):
        self.comment_to_user = dict()
        self.user_to_comments = dict()

    def insert(self, user_idx, comment_idxs, primary_key):
        """
        user_idx : int
        comment_idxs : tuple of int
        primary_key : list of tuple (comment idx, timestamp)
        """
        for cidx in comment_idxs:
            # insert user to `comment to user`
            userset = self.comment_to_user.get(cidx, set())
            userset.add(user_idx)
            self.comment_to_user[cidx] = userset
        # insert comments to `user to comments`
        self.user_to_comments[user_idx] = primary_key


######################
## making directing ##

def make_directing(data_dir, movie_indices, dataset_dir):
    people_dictionary_path = f'{dataset_dir}/peoples.txt'
    directings_path = f'{dataset_dir}/directings.csv'

    # {idx:(kor name, original name)}
    people_dictionary = {}
    if os.path.exists(people_dictionary_path):
        with open(people_dictionary_path, encoding='utf-8') as f:
            next(f)
            for row in f:
                idx, kor, eng = row[:-1].split('\t')
                people_dictionary[int(idx)] = (kor, eng)

    # (movie idx, people idx)
    directings = []

    n_movies = len(movie_indices)
    for i, movie_idx in enumerate(movie_indices):

        path = f'{data_dir}/directors/{movie_idx}'
        if not os.path.exists(path):
            continue

        rows = load_list_of_dict(path)

        for row in rows:
            # load data
            people_idx = row['id']
            # exception: (no link director)
            if isinstance(people_idx, list) and (not people_idx):
                continue
            people_idx = int(people_idx)
            name = (row['k_name'], row.get('e_name', ''))

            # append
            people_dictionary[people_idx] = name
            directings.append((movie_idx, people_idx))

        if i % 5000 == 0:
            percent = 100 * (i+1) / n_movies
            n_peoples = len(people_dictionary)
            n_directings = len(directings)
            print(f'\rScanning {percent:.4}%: {n_peoples} peoples & {n_directings} directings from {n_movies} movies', end='')
    print(f'\rScanning has been finished. Found {n_peoples} peoples & {n_directings} directings from {n_movies} movies')

    save_rows(directings, directings_path, 'movie,people', ',')
    people_dictionary = [(idx, names[0], names[1]) for idx, names in sorted(people_dictionary.items())]
    save_rows(people_dictionary, people_dictionary_path, 'people\tkorean\toriginal', '\t')

####################
## making casting ##

def make_casting(data_dir, movie_indices, dataset_dir):
    people_dictionary_path = f'{dataset_dir}/peoples.txt'
    castings_path = f'{dataset_dir}/castings.csv'
    roles_paths = f'{dataset_dir}/roles.txt'

    # (movie idx, people idx, credit order, leading)
    castings = []
    # (movie idx, people idx, role name)
    roles = []

    # {idx:(kor name, original name)}
    people_dictionary = {}
    if os.path.exists(people_dictionary_path):
        with open(people_dictionary_path, encoding='utf-8') as f:
            next(f)
            for row in f:
                idx, kor, eng = row[:-1].split('\t')
                people_dictionary[int(idx)] = (kor, eng)

    n_movies = len(movie_indices)
    for i, movie_idx in enumerate(movie_indices):

        path = f'{data_dir}/actors/{movie_idx}'
        if not os.path.exists(path):
            continue

        rows = load_list_of_dict(path)

        for row in rows:
            # load data
            people_idx = row['id']
            # exception: (no link director)
            if isinstance(people_idx, list) and (not people_idx):
                continue
            people_idx = int(people_idx)
            name = (row['k_name'], row.get('e_name', ''))
            leading = 1 if row['part'].strip() == '주연' else 0
            role = row.get('role', '').strip()
            if role[-2:] == ' 역':
                role = role[:-2].strip()
            order = row.get('casting_order', row.get('cating_order', -1))

            # append
            people_dictionary[people_idx] = name
            castings.append((movie_idx, people_idx, order, leading))
            roles.append((movie_idx, people_idx, role))

        if i % 5000 == 0:
            percent = 100 * (i+1) / n_movies
            n_peoples = len(people_dictionary)
            n_castings = len(castings)
            print(f'\rScanning {percent:.4}%: {n_peoples} peoples & {n_castings} castings from {n_movies} movies', end='')
    print(f'\rScanning has been finished. Found {n_peoples} peoples & {n_castings} castings from {n_movies} movies\n')

    save_rows(castings, castings_path, 'movie,people,order,leading', ',')
    save_rows(roles, roles_paths, 'movie\tpeople\trole', '\t')
    people_dictionary = [(idx, names[0], names[1]) for idx, names in sorted(people_dictionary.items())]
    save_rows(people_dictionary, people_dictionary_path, 'people\tkorean\toriginal', '\t')

#################
## making meta ##

def make_meta(data_dir, movie_indices, dataset_dir):
    genres_path = f'{dataset_dir}/genres.csv'
    dates_path = f'{dataset_dir}/dates.csv'
    countries_path = f'{dataset_dir}/countries.csv'
    movies_path = f'{dataset_dir}/movies.txt'

    n_movies = len(movie_indices)
    # (movie idx, genre)
    genres = []
    # (movie idx, date)
    dates = []
    # (movie idx, country)
    countries = []
    # (movie idx, title, title eng, year, grade)
    movies = []

    for i, movie_idx in enumerate(movie_indices):
        inpath = f'{data_dir}/meta/{movie_idx}.json'
        if not os.path.exists(inpath):
            continue
        with open(inpath, encoding='utf-8') as f:
            data = json.load(f)

        title = data['title']
        title_eng = data.get('e_title', '')
        grade = data.get('grade', '')
        genres_i = data.get('genres', [])
        dates_i = data.get('open_date', [])
        year = ''
        if dates_i:
            year = dates_i[0][:4]
        countries_i = data.get('countries', [])

        movies.append((movie_idx, title, title_eng, year, grade))
        for g in genres_i:
            genres.append((movie_idx, g))
        for d in dates_i:
            dates.append((movie_idx, d))
        for c in countries_i:
            countries.append((movie_idx, c))

        if i % 5000 == 0:
            percent = 100 * (i+1) / n_movies
            print(f'\rScanning metadata: {percent:.4}% from {i+1} / {n_movies} movies', end='')
    print(f'\rScanning metadata was finished with {n_movies} movies{" "*20}\n')

    save_rows(genres, genres_path, 'movie,genre', ',')
    save_rows(dates, dates_path, 'movie,date', ',')
    save_rows(countries, countries_path, 'movie,country', ',')
    save_rows(movies, movies_path, 'movie\ttitle\ttitle_eng\tyear\tgrade', '\t')
