import json
from .utils import initialize_usermapper
from .utils import save_usermapper
from .utils import load_usermapper
from .utils import load_list_of_dict
from .utils import mask_user
from .utils import to_unix_time

def make_ratings(data_dir, movie_indices, dataset_dir):

    def row_to_str(row, delimiter=','):
        return delimiter.join([str(v) for v in row])

    texts_path = f'{dataset_dir}/texts.txt'
    rates_path = f'{dataset_dir}/rates.csv'
    userlist_path = f'{dataset_dir}/userlist'
    user_id_mapper = initialize_usermapper(load_usermapper(userlist_path))

    n_movies = len(movie_indices)
    rates_dumps = []
    texts_dumps = []
    for i, movie_idx in enumerate(movie_indices):
        inpath = f'{data_dir}/comments/{movie_idx}'
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
