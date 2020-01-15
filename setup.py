import kmr_dataset
from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="kmr_dataset",
    version=kmr_dataset.__version__,
    author=kmr_dataset.__author__,
    author_email='soy.lovit@gmail.com',
    url='https://github.com/lovit/kmrd',
    description="Korean Movie Recommender system Dataset",
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=["scipy>=1.1.0", "numpy>=1.17.4"],
    keywords = ['Recommender system dataset'],
    packages=find_packages(),
    package_data={
        'kmr_dataset':['datafile/kmrd-small/*', 'datafile/kmrd/*.zip']
    },
)
