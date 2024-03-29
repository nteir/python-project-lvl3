from page_loader.page_loader import FileSystemError, PageDownloadError, parse_arguments, download, download_resources_threading, get_html_content
from bs4 import BeautifulSoup
import os.path
import os
import sys
from concurrent import futures
from progress.bar import Bar
import tempfile
import requests_mock as req_mock
import pytest

source_url = 'http://testnetloc.com/some/path/fake_test.html'
file_name = 'testnetloc-com-some-path-fake_test.html'
scheme = 'http'
domain = 'testnetloc.com'
with open('./tests/fixtures/fake_test.html') as file:
    content = file.read()
with open('./tests/fixtures/expected.html') as file:
    expected_content = file.read()
resources = [
    'http://testnetloc.com/pics/pic1.jpg',
    'http://testnetloc.com/pics/pic2.png',
    'http://testnetloc.com/style/style.css',
]
to_download = {
    'testnetloc-com-pics-pic1.jpg': 'http://testnetloc.com/pics/pic1.jpg',
    'testnetloc-com-pics-pic2.png': '/pics/pic2.png',
    'testnetloc-com-style-style.css': '/style/style.css',
}
STATUS_CODES = [204, 403, 404, 500, 503]
ARGV = [
    ['page-loader', '--output', '/home/user0/output', source_url],
    ['page-loader', source_url],
]
ARGS = [
    (source_url, '/home/user0/output'),
    (source_url, None),
]


@pytest.mark.parametrize("argv,args", zip(ARGV, ARGS))
def test_parse_args(argv, args):
    sys.argv = argv
    received_args = parse_arguments()
    expected_source, expected_output = args
    assert received_args.source == expected_source
    assert received_args.output == expected_output


def mock_matcher(request):
    url = request.url
    mocked_urls = list(resources)
    return url in mocked_urls


def test_download(requests_mock):
    requests_mock.get(source_url, text=content)
    requests_mock.get(
        req_mock.ANY,  # Mock any URL before matching
        additional_matcher=mock_matcher,  # Mock only matched
        text="Some fake response",
    )
    with tempfile.TemporaryDirectory() as tmpdirname:
        received_name = download(source_url, tmpdirname)
        assert os.path.isfile(received_name)
        received_path, received_file_name = os.path.split(received_name)
        assert os.path.abspath(received_path) == os.path.abspath(tmpdirname)
        assert received_file_name == file_name
        with open(received_name) as f:
            received_content = f.read()
            assert BeautifulSoup(received_content, features="html.parser").prettify() == BeautifulSoup(expected_content, features="html.parser").prettify()


def test_default_download(requests_mock):
    requests_mock.get(source_url, text='content')
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)
        received_name = download(source_url)
        received_path = os.path.dirname(received_name)
        assert os.path.abspath(received_path) == os.path.abspath(tmpdirname)


def test_download_resources(requests_mock):
    requests_mock.get(
        req_mock.ANY,  # Mock any URL before matching
        additional_matcher=mock_matcher,  # Mock only matched
        text="Some fake response",
    )
    with tempfile.TemporaryDirectory() as tmpdirname:
        bar = Bar('Downloading', max=len(to_download))
        with futures.ThreadPoolExecutor(max_workers=8) as executor:
            for file_name, source_file_path in to_download.items():
                executor.submit(download_resources_threading, file_name, source_file_path, domain, scheme, tmpdirname, bar)
        for resource in to_download.keys():
            path = os.path.join(tmpdirname, resource)
            assert os.path.isfile(path)


def test_exc_nodir_download():
    dest_dir = 'notadir'
    with pytest.raises(FileSystemError):
        download(source_url, dest_dir)


@pytest.mark.parametrize("status_codes", STATUS_CODES)
def test_err_get_html_content(requests_mock, status_codes):
    requests_mock.get(source_url, text='', status_code=status_codes)
    with pytest.raises(PageDownloadError):
        get_html_content(source_url)
