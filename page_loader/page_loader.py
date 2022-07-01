import os
import re
from urllib.parse import urlparse, urlunparse
import requests
from bs4 import BeautifulSoup
import logging
from progress.bar import Bar
import argparse

TAGS = {
    'img': 'src',
    'link': 'href',
    'script': 'src',
}


class BaseOSError(OSError):
    pass


def parse_args():
    parser = argparse.ArgumentParser(
        description='Downloads a Web page and saves it locally.'
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="destination directory path"
    )
    parser.add_argument("source")
    return parser.parse_args()


def download(source_url, dest_path=None):
    if dest_path is None:
        dest_path = os.getcwd()
    split_url = urlparse(source_url)
    domain = split_url.netloc
    scheme = split_url.scheme
    dest_file_name, resource_dir_name = get_output_path(source_url)
    dest_file_path = os.path.join(dest_path, dest_file_name)

    if not os.path.isdir(dest_path):
        logging.error(
            f'Destination path set to {dest_path}, not an existing directory'
        )
        raise BaseOSError(
            'Destination path must be an existing directory'
        )

    html = get_html_content(source_url)
    pretty_html, to_download = process_html(
        html, domain, scheme, resource_dir_name
    )
    try:
        with open(dest_file_path, 'w') as output_html:
            output_html.write(pretty_html)
    except OSError as e:
        logging.error('Error creating file.')
        raise BaseOSError() from e

    if to_download:
        resource_path = os.path.join(dest_path, resource_dir_name)
        create_resource_dir(resource_path)
        download_resources(to_download, domain, scheme, resource_path)
    return dest_file_path


def create_resource_dir(dest_path):
    if not os.path.isdir(dest_path):
        try:
            os.mkdir(dest_path)
        except OSError as e:
            logging.error('Error creating directory.')
            raise BaseOSError() from e


def get_html_content(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            logging.error(
                f'HTTP Error, status code: {r.status_code}'
            )
            raise BaseOSError()
    except OSError as e:
        logging.error('Connection error.')
        raise BaseOSError() from e
    return r.text


def get_output_path(source_url):
    split_url = urlparse(source_url)
    url_path, _ = os.path.splitext(split_url.path)
    common_string = re.sub(r'[\W^_]', '-', split_url.netloc)
    path_string = '-'.join(filter(None, url_path.split('/')))
    common_string = '-'.join(filter(None, (common_string, path_string)))
    resource_dir_name = f'{common_string}_files'
    dest_file_name = f'{common_string}.html'
    return dest_file_name, resource_dir_name


def is_a_resource(tag):
    return tag.name in TAGS and tag.has_attr(TAGS[tag.name])


def process_html(text, domain, scheme, resource_local_path):
    soup = BeautifulSoup(text, 'html.parser')
    to_download = {}
    resources = soup.find_all(is_a_resource)
    for tag in resources:
        attribute_link = tag[TAGS[tag.name]]    # src or href value
        split_url = urlparse(attribute_link)
        if split_url.netloc == '' or split_url.netloc == domain:
            resource_url = urlunparse(
                (scheme, domain, split_url.path, '', '', '')
            )
            file_name = get_new_filename(resource_url)
            to_download[file_name] = attribute_link
            tag[TAGS[tag.name]] = f'{resource_local_path}/{file_name}'
    return soup.prettify(), to_download


def get_new_filename(url):
    split_url = urlparse(url)
    url_path, url_ext = os.path.splitext(split_url.path)
    if not url_ext:
        url_ext = '.html'
    file_name_string = f'{split_url.netloc}{url_path}'
    file_name_string = re.sub(r'[\W^_]', '-', file_name_string)
    file_name_string = f'{file_name_string}{url_ext}'
    return file_name_string


def download_resources(files, domain, scheme, dest_path):
    bar = Bar('Downloading', max=len(files))
    for file_name, source_file_path in files.items():
        source_path = source_file_path
        url = urlparse(source_file_path)
        if url.netloc == '':
            source_path = urlunparse(
                (scheme, domain, source_file_path, '', '', '')
            )
        dest_file_path = os.path.join(dest_path, file_name)
        try:
            r = requests.get(source_path, stream=True)
            write_res_file(r, dest_file_path, source_path)
        except OSError as e:
            log_str = e.message if hasattr(e, 'message') else e
            logging.debug(log_str)
            logging.warning('Failed to access a resource file.')
        bar.next()
    bar.finish()


def write_res_file(req, dest_file_path, source_file_path):
    if req.status_code == 200:
        with open(dest_file_path, 'wb') as resource_file:
            for chunk in req:
                resource_file.write(chunk)
    else:
        logging.debug(
            f'Error accessing {source_file_path}, code {req.status_code}'
        )
        logging.warning('Failed to access a resource file.')
