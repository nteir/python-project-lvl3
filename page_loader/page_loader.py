import os
import re
from urllib.parse import urlparse
import urllib.request


def download(source_path, dest_path):
    if dest_path is None:
        dest_path = os.getcwd()
    dest_name = get_output_path(source_path, dest_path)
    with urllib.request.urlopen(source_path) as html_file:
        if os.path.exists(dest_path):
            with open(dest_name, 'w') as output_html:
                for line in html_file:
                    output_html.write(line.decode('utf-8'))
    return dest_name


def get_output_path(source_path, dest_path):
    url = urlparse(source_path)
    url_path, _ = os.path.splitext(url.path)
    url_path = '-'.join(filter(None, url_path.split('/')))
    dest_name = re.sub(r'[\W^_]', '-', url.netloc)
    dest_name += f'-{url_path}.html'
    dest_name = os.path.join(dest_path, dest_name)
    return dest_name
