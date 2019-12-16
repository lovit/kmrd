import json
import os
from collections import defaultdict
from datetime import datetime


def to_unix_time(time_strf):
    return int(datetime.strptime(time_strf, '%Y.%m.%d %H:%M').timestamp())

def initialize_usermapper(mapper=None):
    user_id_mapper = defaultdict(lambda: len(user_id_mapper))
    if mapper is not None:
        user_id_mapper.update(mapper)
    return user_id_mapper

def mask_user(user, mapper):
    return mapper[user]

def save_usermapper(mapper, path):
    user_list = sorted(mapper, key=lambda u:mapper[u])
    with open(path, 'w', encoding='utf-8') as f:
        for user in user_list:
            f.write(f'{user}\n')

def load_usermapper(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding='utf-8') as f:
        user_id_mapper = {user.strip():idx for idx, user in enumerate(f)}
    return user_id_mapper

def load_list_of_dict(path):
    """
    Arguments
    ---------
    path : str
        File path

    Returns
    -------
    obj : list of dict
        Object to store
    """

    with open(path, encoding='utf-8') as f:
        objs = [json.loads(obj.strip()) for obj in f]
    return objs