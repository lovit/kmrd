import os
import json
from .utils import initialize_usermapper
from .utils import save_usermapper
from .utils import load_usermapper
from .utils import load_list_of_dict
from .utils import mask_user
from .utils import to_unix_time

def row_to_str(row, delimiter=','):
    return delimiter.join([str(v) for v in row])

def make_ratings(data_dir, movie_indices, dataset_dir):
    texts_path = f'{dataset_dir}/texts.txt'
    rates_path = f'{dataset_dir}/rates.csv'
    userlist_path = f'{dataset_dir}/userlist'
    user_id_mapper = initialize_usermapper(load_usermapper(userlist_path))

    n_movies = len(movie_indices)
    rates_dumps = []
    texts_dumps = []
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
        n_rates = len(rates_dumps)
        n_texts = len(texts_dumps)
        print(f'Scanned {n_rates} rates & {n_texts} texts from {i+1} / {n_movies} movies')

    rates_dumps = sorted(rates_dumps)
    texts_dumps = sorted(texts_dumps)

    with open(rates_path, 'w', encoding='utf-8') as f:
        f.write(f'user,movie,rate,time\n')
        for row in rates_dumps:
            row_strf = row_to_str(row, delimiter=',')
            f.write(f'{row_strf}\n')

    with open(texts_path, 'w', encoding='utf-8') as f:
        f.write('user\tmovie\tagree\tdisagree\ttext\n')
        for row in texts_dumps:
            row_strf = row_to_str(row, delimiter='\t')
            f.write(f'{row_strf}\n')

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
            n_peoples = len(people_dictionary)
            n_directings = len(directings)
            print(f'Scanned {n_peoples} peoples & {n_directings} directings from {i+1}/{n_movies} movies')

    with open(directings_path, 'w', encoding='utf-8') as f:
        f.write('movie,people\n')
        for row in directings:
            row_strf = row_to_str(row, delimiter=',')
            f.write(f'{row_strf}\n')

    people_dictionary = [(idx, names[0], names[1]) for idx, names in sorted(people_dictionary.items())]
    with open(people_dictionary_path, 'w', encoding='utf-8') as f:
        f.write('people\tkorean\toriginal\n')
        for row in people_dictionary:
            row_strf = row_to_str(row, delimiter='\t')
            f.write(f'{row_strf}\n')

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
            n_peoples = len(people_dictionary)
            n_castings = len(castings)
            print(f'Scanned {n_peoples} peoples & {n_castings} castings from {i+1}/{n_movies} movies')

    with open(castings_path, 'w', encoding='utf-8') as f:
        f.write('movie,people,order,major\n')
        for row in castings:
            row_strf = row_to_str(row, delimiter=',')
            f.write(f'{row_strf}\n')

    with open(roles_paths, 'w', encoding='utf-8') as f:
        f.write('movie\tpeople\trole\n')
        for row in roles:
            row_strf = row_to_str(row, delimiter='\t')
            f.write(f'{row_strf}\n')

    people_dictionary = [(idx, names[0], names[1]) for idx, names in sorted(people_dictionary.items())]
    with open(people_dictionary_path, 'w', encoding='utf-8') as f:
        f.write('people\tkorean\toriginal\n')
        for row in people_dictionary:
            row_strf = row_to_str(row, delimiter='\t')
            f.write(f'{row_strf}\n')

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
    # (movie idx, title, title eng, grade)
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
        countries_i = data.get('countries', [])

        movies.append((movie_idx, title, title_eng, grade))
        for g in genres_i:
            genres.append((movie_idx, g))
        for d in dates_i:
            dates.append((movie_idx, d))
        for c in countries_i:
            countries.append((movie_idx, c))

        if i % 100 == 0:
            print(f'Scanned metadata from {i+1} / {n_movies} movies')

    with open(genres_path, 'w', encoding='utf-8') as f:
        f.write(f'movie,genre\n')
        for row in genres:
            row_strf = row_to_str(row, delimiter=',')
            f.write(f'{row_strf}\n')

    with open(dates_path, 'w', encoding='utf-8') as f:
        f.write(f'movie,date\n')
        for row in dates:
            row_strf = row_to_str(row, delimiter=',')
            f.write(f'{row_strf}\n')

    with open(countries_path, 'w', encoding='utf-8') as f:
        f.write(f'movie,country\n')
        for row in countries:
            row_strf = row_to_str(row, delimiter=',')
            f.write(f'{row_strf}\n')

    with open(movies_path, 'w', encoding='utf-8') as f:
        f.write(f'movie\ttitle\ttitle_eng\tgrade\n')
        for row in movies:
            row_strf = row_to_str(row, delimiter='\t')
            f.write(f'{row_strf}\n')