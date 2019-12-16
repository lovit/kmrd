import os
import json
from .utils import initialize_usermapper
from .utils import save_usermapper
from .utils import save_rows
from .utils import load_usermapper
from .utils import load_list_of_dict
from .utils import mask_user
from .utils import to_unix_time

def make_ratings(data_dir, movie_indices, dataset_dir):
    texts_path = f'{dataset_dir}/texts.txt'
    rates_path = f'{dataset_dir}/rates.csv'
    userlist_path = f'{dataset_dir}/userlist'
    user_id_mapper = initialize_usermapper(load_usermapper(userlist_path))

    rates_dumps = []
    texts_dumps = []

    n_movies = len(movie_indices)
    for i, movie_idx in enumerate(movie_indices):
        inpath = f'{data_dir}/comments/{movie_idx}'
        if not os.path.exists(inpath):
            continue
        comments = load_list_of_dict(inpath)
        comments = {json.dumps(row) for row in comments}
        comments = [json.loads(row) for row in comments]
        rates = []
        texts = []

        for comment in comments:
            user_idx = mask_user(comment['user'], user_id_mapper)
            timestamp = to_unix_time(comment['written_at'])
            rate = comment['score']
            text = comment['text']
            agree, disagree = comment['agree'], comment['disagree']

            rates.append((user_idx, movie_idx, rate, timestamp))
            if text:
                texts.append((user_idx, movie_idx, agree, disagree, text))

        rates_dumps += rates
        texts_dumps += texts

        if i % 100 == 0:
            percent = 100 * (i+1) / n_movies
            n_rates = len(rates_dumps)
            n_texts = len(texts_dumps)
            print(f'\rScanning {percent:.4}%: {n_rates} rates & {n_texts} texts from {n_movies} movies', end='')
    print(f'\rScanning has been finished. Found {n_rates} rates & {n_texts} texts from {n_movies} movies')

    rates_dumps = sorted(rates_dumps)
    texts_dumps = sorted(texts_dumps)

    save_rows(rates_dumps, rates_path, 'user,movie,rate,time', ',')
    save_rows(texts_dumps, texts_path, 'user\tmovie\tagree\tdisagree\ttext', '\t')
    save_usermapper(user_id_mapper, userlist_path)

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
            people_idx = int(row['id'])
            name = (row['k_name'], row.get('e_name', ''))

            # append
            people_dictionary[people_idx] = name
            directings.append((movie_idx, people_idx))

        if i % 100 == 0:
            percent = 100 * (i+1) / n_movies
            n_peoples = len(people_dictionary)
            n_directings = len(directings)
            print(f'\rScanning {percent:.4}%: {n_peoples} peoples & {n_directings} directings from {n_movies} movies', end='')
    print(f'\rScanning has been finished. Found {n_peoples} peoples & {n_directings} directings from {n_movies} movies')

    save_rows(directings, directings_path, 'movie,people', ',')
    people_dictionary = [(idx, names[0], names[1]) for idx, names in sorted(people_dictionary.items())]
    save_rows(people_dictionary, people_dictionary_path, 'people\tkorean\toriginal', '\t')

def make_casting(data_dir, movie_indices, dataset_dir):
    people_dictionary_path = f'{dataset_dir}/peoples.txt'
    castings_path = f'{dataset_dir}/castings.csv'
    roles_paths = f'{dataset_dir}/roles.txt'

    # (movie idx, people idx, credit order, major)
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
            people_idx = int(row['id'])
            name = (row['k_name'], row.get('e_name', ''))
            major = 1 if row['part'].strip() == '주연' else 0
            role = row.get('role', '').strip()
            if role[-2:] == ' 역':
                role = role[:-2].strip()
            order = row.get('casting_order', row['cating_order'])

            # append
            people_dictionary[people_idx] = name
            castings.append((movie_idx, people_idx, order, major))
            roles.append((movie_idx, people_idx, role))

        if i % 100 == 0:
            percent = 100 * (i+1) / n_movies
            n_peoples = len(people_dictionary)
            n_castings = len(castings)
            print(f'\rScanning {percent:.4}%: {n_peoples} peoples & {n_castings} castings from {n_movies} movies', end='')
    print(f'\rScanning has been finished. Found {n_peoples} peoples & {n_castings} castings from {n_movies} movies')

    save_rows(castings, castings_path, 'movie,people,order,major', ',')
    save_rows(roles, roles_paths, 'movie\tpeople\trole', '\t')
    people_dictionary = [(idx, names[0], names[1]) for idx, names in sorted(people_dictionary.items())]
    save_rows(people_dictionary, people_dictionary_path, 'people\tkorean\toriginal', '\t')

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

        if i % 100 == 0:
            percent = 100 * (i+1) / n_movies
            print(f'\rScanning metadata: {percent:.4}% from {i+1} / {n_movies} movies', end='')
    print(f'\rScanning metadata was finished with {n_movies} movies{" "*20}')

    save_rows(genres, genres_path, 'movie,genre', ',')
    save_rows(dates, dates_path, 'movie,date', ',')
    save_rows(countries, countries_path, 'movie,country', ',')
    save_rows(movies, movies_path, 'movie\ttitle\ttitle_eng\tyear\tgrade', '\t')
