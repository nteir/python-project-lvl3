import os
import sys
import re
from urllib.parse import urlparse, urlunparse
import requests
from bs4 import BeautifulSoup
import logging

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
        logging.error(
            f'Destination path set to {dest_path}, not an existing directory'
        )
        raise NotADirectoryError(
            'Destination path must be an existing directory'
        )
    html = get_html_content(source_path)
    pretty_html, to_download = process_html(html, domain, resource_dir)
    if to_download:
        dest_dir = os.path.join(dest_path, resource_dir)
        if not os.path.isdir(dest_dir):
            try:
                os.mkdir(dest_dir)
            except OSError:
                logging.error('Error creating directory.')
                sys.exit(1)
        download_resources(to_download, domain, dest_dir)
    with open(dest_file, 'w') as output_html:
        output_html.write(pretty_html)
    return dest_file


def get_html_content(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.text
        else:
            logging.error(
                f'Error on HTTP request, status code: {r.status_code}'
            )
            raise ConnectionError
    except (OSError, ConnectionError) as e:
        log_str = e.message if hasattr(e, 'message') else e
        logging.debug(log_str)
        logging.error('Error accessing the WEB page, check if URL is correct.')
        sys.exit(1)


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
        try:
            r = requests.get(source_path, stream=True)
            if r.status_code == 200:
                with open(dest_path, 'wb') as resource_file:
                    for chunk in r:
                        resource_file.write(chunk)
            else:
                logging.debug(
                    f'Error accessing {source_path}, code {r.status_code}'
                )
                logging.warning('Failed to access a resource file.')
        except (OSError, ConnectionError) as e:
            log_str = e.message if hasattr(e, 'message') else e
            logging.debug(log_str)
            logging.warning('Failed to access a resource file.')
