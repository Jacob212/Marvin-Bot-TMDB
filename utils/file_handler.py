import re
from gzip import open as gzopen
from os import remove, mkdir, path, walk
from datetime import datetime, timedelta
from requests import get
import json

_EXPORTS = ["movie_ids", "tv_series_ids", "person_ids", "collection_ids", "tv_network_ids", "keyword_ids", "production_company_ids"]

def _set_time():
    date = datetime.utcnow()
    if date.hour <= 8:
        date = date-timedelta(1)
    return date

def _make_dir(location):
    if not path.isdir(f'./{location}'):
        mkdir(f'./{location}')

def get_file_names(location):
    if path.isdir(f'./{location}'):
        files = []
        for r, d, f in walk(f'./{location}'):
            for file in f:
                if '.json' in file:
                    files.append(file[:-5])
        return files
    return "nothing"

def download(location):
    _make_dir(location)
    date = _set_time()
    if date is not None:
        for export in _EXPORTS:
            response = get(f'http://files.tmdb.org/p/exports/{export}_{date.strftime("%m")}_{date.strftime("%d")}_{date.year}.json.gz', stream=True)
            with open(f'./{location}/{export}.json.gz', "wb") as f:
                for chunk in response.iter_content(1024):
                    if chunk:
                        f.write(chunk)

            with gzopen(f'./{location}/{export}.json.gz', mode="rt", encoding="utf-8") as file:
                basic = file.readlines()
            remove(f'./{location}/{export}.json.gz')
            with open(f'./{location}/{export}.json', "w", encoding="utf-8") as f:
                for line in basic:
                    f.write(line)

def find_exact(location, file, find):
    key = "name"
    if file == "movie_ids":
        key = "original_title"
    elif file == "tv_series_ids":
        key = "original_name"
    with open(f'./{location}/{file}.json', mode="r", encoding="utf-8") as f:
        for rownum, line in enumerate(f):
            if find.lower() == json.loads(line)[key]:
                return json.loads(line)
    return None

def find_all(location, file, find):
    found = []
    key = "name"
    if file == "movie_ids":
        key = "original_title"
    elif file == "tv_series_ids":
        key = "original_name"
    with open(f'./{location}/{file}.json', mode="r", encoding="utf-8") as f:
        for rownum, line in enumerate(f):
            if re.search(rf'\b{find}', json.loads(line)[key], re.IGNORECASE) is not None:
                found.append(json.loads(line))
    return found
