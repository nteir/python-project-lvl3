import os
import re
from urllib.parse import urlparse
import requests


def download(source_path, dest_path):
    if dest_path is None:
        dest_path = os.getcwd()
    dest_name = get_output_path(source_path, dest_path)
    if os.path.isdir(dest_path):
        r = requests.get(source_path)
        with open(dest_name, 'w') as output_html:
            output_html.write(r.text)
    else:
        raise NotADirectoryError(
            'Destination path must be an existing directory'
        )
    return dest_name


def get_output_path(source_path, dest_path):
    url = urlparse(source_path)
    url_path, _ = os.path.splitext(url.path)
    url_path = '-'.join(filter(None, url_path.split('/')))
    dest_name = re.sub(r'[\W^_]', '-', url.netloc)
    dest_name += f'-{url_path}.html'
    dest_name = os.path.join(dest_path, dest_name)
    return dest_name
