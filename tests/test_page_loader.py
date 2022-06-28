from page_loader.page_loader import BaseOSError, download, download_resources, get_html_content
from bs4 import BeautifulSoup
import os.path
import os
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


def mock_matcher(request):
    url = request.url
    mocked_urls = []
    for resource in resources:
        mocked_urls.append(resource)
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
        download_resources(to_download, domain, scheme, tmpdirname)
        for resource in to_download.keys():
            path = os.path.join(tmpdirname, resource)
            assert os.path.isfile(path)


def test_exc_nodir_download():
    dest_dir = 'notadir'
    with pytest.raises(BaseOSError):
        download(source_url, dest_dir)


@pytest.fixture(name="status_codes", params=STATUS_CODES)
def _test_params(request):
    return request.param


def test_err_get_html_content(requests_mock, status_codes):
    requests_mock.get(source_url, text='', status_code=status_codes)
    with pytest.raises(BaseOSError):
        get_html_content(source_url)
