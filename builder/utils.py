import json
import os
from collections import defaultdict
from datetime import datetime


def to_unix_time(time_strf):
    """
    Arguments
    ---------
    time_strf : str
        YYYY.mm.dd HH;MM form. For example,

            2019-01-23 12:34

    Returns
    -------
    time : int
        Unix time
    """
    return int(datetime.strptime(time_strf, '%Y.%m.%d %H:%M').timestamp())

def initialize_usermapper(mapper=None):
    """
    Maker dict as defaultdict.
    """
    user_id_mapper = defaultdict(lambda: len(user_id_mapper))
    if mapper is not None:
        user_id_mapper.update(mapper)
    return user_id_mapper

def mask_user(user, mapper):
    """
    Arguments
    ---------
    user : str
        User name or identifier
    mapper : defaultdict

    Returns
    -------
    index : int
        If the mapper has user as key, it returns corresponding value (index)
        Else, it returns len(mapper) as index of the user
    """
    return mapper[user]

def save_usermapper(mapper, path):
    """
    Arguments
    ---------
    mapper : dict
        mapper['user'] = index
    path : str
        User index path
        It store user list as sorted list form
    """
    user_list = sorted(mapper, key=lambda u:mapper[u])
    with open(path, 'w', encoding='utf-8') as f:
        for user in user_list:
            f.write(f'{user}\n')

def load_usermapper(path):
    """
    Arguments
    ---------
    path : str
        User index path
        List of users form. For example, 

            8215405
            446931
            5021627
            2674713
            ...

    Returns
    -------
    user_id_mapper : dict
        user_id_mapper['user'] = index
    """
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

def save_rows(rows, path, header, delimiter):
    """
    Arguments
    ---------
    rows : list of tuple
        For example, 

            [(movie id, title, ... ),
             (movie id, title, ... ),
             ...
            ]

    path : str
        File path to save rows
    header : str
        Column names
    delimiter : str
        Column separator
    """
    def row_to_str(row, delimiter=','):
        return delimiter.join([str(v) for v in row])

    with open(path, 'w', encoding='utf-8') as f:
        f.write(f'{header}\n')
        for row in rows:
            f.write(f'{row_to_str(row, delimiter=delimiter)}\n')
