import os
import re
from urllib.parse import urlparse, urlunparse
import requests
from bs4 import BeautifulSoup

TAGS = {
    'img': 'src',
    'link': 'href',
    'script': 'src',
}


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
    common_string = re.sub(r'[\W^_]', '-', url.netloc)
    path_string = '-'.join(filter(None, url_path.split('/')))
    common_string = '-'.join(filter(None, (common_string, path_string)))
    resource_dir = f'{common_string}_files'
    dest_name = f'{common_string}.html'
    return dest_name, resource_dir


def is_a_resource(tag):
    return tag.name in TAGS and tag.has_attr(TAGS[tag.name])


def process_html(text, domain, resource_dir):
    soup = BeautifulSoup(text, 'html.parser')
    to_download = {}
    resources = soup.find_all(is_a_resource)
    for tag in resources:
        attribute_link = tag[TAGS[tag.name]]
        link_parse = urlparse(attribute_link)
        if link_parse.netloc == '' or link_parse.netloc == domain:
            resource_path = urlunparse(
                ('http', domain, link_parse.path, '', '', '')
            )
            filename = get_new_filename(resource_path)
            to_download[filename] = attribute_link
            tag[TAGS[tag.name]] = f'{resource_dir}/{filename}'
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
