import os
import zipfile


installpath = os.path.abspath(os.path.dirname(__file__))
patch_urls = {}

def _check_install(paths, size):
    if size == 'small':
        for path in paths:
            if not os.path.exists(path):
                name = path.split("/")[-1]
                raise ValueError(f'Reinstall KMRD package. {name} is not found')
        return True

    metazip_path = f'{installpath}/datafile/kmrd/meta.zip'
    ratezip_path = f'{installpath}/datafile/kmrd/rates-{size}.zip'
    for path in paths:
        if not os.path.exists(path):
            if path.split('/')[-1][:5] == 'rates':
                if not os.path.exists(metazip_path):
                    raise ValueError(f'Reinstall KMRD package. meta.zip is not found')
                unzip(ratezip_path, f'{installpath}/datafile/kmrd/')
                print(f'Unzipped rates-{size}.zip')
            else:
                if not os.path.exists(ratezip_path):
                    raise ValueError(f'Reinstall KMRD package. rates-{size}.zip is not found')
                unzip(metazip_path, f'{installpath}/datafile/kmrd/')
                print('Unzipped meta.zip')
    return True

def unzip(source, destination):
    """
    Arguments
    ---------
    source : str
        zip file address. It doesn't matter absolute path or relative path
    destination :
        Directory path of unzip
    Returns
    -------
    flag : Boolean
        It return True if downloading success else return False
    """

    abspath = os.path.abspath(destination)
    dirname = os.path.dirname(abspath)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    try:
        downloaded = zipfile.ZipFile(source)
        downloaded.extractall(destination)
        return True
    except Exception as e:
        print(e)
        return False

def download_a_file(url, fname):
    """
    Arguments
    --------
    url : str
        URL address of file to be downloaded
    fname : str
        Download file address
    Returns
    -------
    flag : Boolean
        It return True if downloading success else return False
    """

    fname = os.path.abspath(fname)
    dirname = os.path.dirname(fname)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    # If you do not set user-agent, downloading from url is stalled.
    headers = {'user-agent': 'Wget/1.16 (linux-gnu)'}

    try:
        r = requests.get(url, stream=True, headers=headers)
        with open(fname, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        print(e)
        return False
