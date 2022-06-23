import os
import re
from urllib.parse import urlparse, urlunparse
import requests
from bs4 import BeautifulSoup


def download(source_path, dest_path):
    if dest_path is None:
        dest_path = os.getcwd()
    url = urlparse(source_path)
    domain = url.netloc
    dest_name, resource_dir = get_output_path(source_path)
    dest_file = os.path.join(dest_path, dest_name)
    if not os.path.isdir(dest_path):
        raise NotADirectoryError(
            'Destination path must be an existing directory'
        )
    r = requests.get(source_path)
    if r.status_code != 200:
        raise ConnectionError(f'Status code: {r.status_code}')
    pretty_html, to_download = process_html(r.text, domain, resource_dir)
    if to_download:
        dest_dir = os.path.join(dest_path, resource_dir)
        if not os.path.isdir(dest_dir):
            os.mkdir(dest_dir)
        download_resources(to_download, domain, dest_dir)
    with open(dest_file, 'w') as output_html:
        output_html.write(pretty_html)
    return dest_file


def get_output_path(source_path):
    url = urlparse(source_path)
    url_path, _ = os.path.splitext(url.path)
    url_path = '-'.join(filter(None, url_path.split('/')))
    dest_name = re.sub(r'[\W^_]', '-', url.netloc)
    resource_dir = dest_name + f'-{url_path}_files'
    dest_name += f'-{url_path}.html'
    return dest_name, resource_dir


def process_html(text, domain, resource_dir):
    soup = BeautifulSoup(text, 'html.parser')
    images = soup.find_all("img")
    to_download = {}
    for image in images:
        src = image['src']
        src_parse = urlparse(src)
        if src_parse.netloc == '' or src_parse.netloc == domain:
            src_path = urlunparse(('http', domain, src_parse.path, '', '', ''))
            filename = get_new_filename(src_path)
            to_download[filename] = image['src']
            image['src'] = f'{resource_dir}/{filename}'
    return soup.prettify(), to_download


def get_new_filename(path):
    split_path = urlparse(path)
    url_path, url_ext = os.path.splitext(split_path.path)
    src_string = f'{split_path.netloc}{url_path}'
    src_string = re.sub(r'[\W^_]', '-', src_string)
    src_string = f'{src_string}{url_ext}'
    return src_string


def download_resources(files, domain, dest_dir):
    for name, source in files.items():
        source_path = source
        url = urlparse(source)
        if url.netloc == '':
            source_path = urlunparse(('http', domain, source, '', '', ''))
        dest_path = os.path.join(dest_dir, name)
        r = requests.get(source_path, stream=True)
        if r.status_code == 200:
            with open(dest_path, 'wb') as resource_file:
                for chunk in r:
                    resource_file.write(chunk)
