"""
tablite
"""
build_tag = "46d8ab7f1e53cde3b888a99db798ed3e39a57b7f55b39561efcc4210573ab822"
from setuptools import setup
from pathlib import Path


folder = Path(__file__).parent
file = "README.md"
readme = folder / file
assert isinstance(readme, Path)
assert readme.exists(), readme
with open(str(readme), encoding='utf-8') as f:
    long_description = f.read()

keywords = list({
    'tablite', 'tables', 'csv', 'txt', 'excel', 'xlsx', 'ods', 'zip', 'log',
    'any', 'all', 'filter', 'column', 'columns', 'rows', 'from', 'json', 'to',
    'inner join', 'outer join', 'left join', 'groupby', 'pivot', 'pivot tablite',
    'sort', 'is sorted', 'show', 'use disk', 'out-of-memory', 'list on disk',
    'stored list', 'min', 'max', 'sum', 'first', 'last', 'count', 'unique',
    'average', 'standard deviation', 'median', 'mode', 'in-memory', 'index'
})

keywords.sort(key=lambda x: x.lower())

with open('requirements.txt', 'r') as fi:
    requirements = [v.rstrip('\n') for v in fi.readlines()]


setup(
    name="tablite",
    version="2021.3.2.36410",
    url="https://github.com/root-11/tablite",
    license="MIT",
    author="Bjorn Madsen",
    author_email="bjorn.madsen@operationsresearchgroup.com",
    description="A tablite crunching library",
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=keywords,
    packages=["tablite"],
    include_package_data=True,
    data_files=[(".", ["LICENSE", "README.md", "requirements.txt"])],
    platforms="any",
    install_requires=requirements,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)


