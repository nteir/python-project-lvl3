from page_loader.page_loader import download, download_resources
import os.path
import tempfile
import requests_mock as req_mock
import pytest

source_url = 'http://testnetloc.com/some/path/fake_test.html'
file_name = 'testnetloc-com-some-path-fake_test.html'
resource_dir = 'testnetloc-com-some-path-fake_test_files'
domain = 'testnetloc.com'
# with open('./tests/fixtures/fake_test.html') as file:
#     content = file.read()
resources = [
    {
        'url': 'http://testnetloc.com/pics/pic1.jpg',
        'expected_name': 'testnetloc-com-pics-pic1.jpg'
    },
    {
        'url': 'http://testnetloc.com/pics/pic2.png',
        'expected_name': 'testnetloc-com-pics-pic2.png'
    },
]


def test_request_download():
    expected_content = 'sample text'
    with req_mock.Mocker() as mock:
        mock.get(source_url, text=expected_content)
        with tempfile.TemporaryDirectory() as tmpdirname:
            dest_dir = tmpdirname
            expected_name = os.path.join(dest_dir, file_name)
            received_name = download(source_url, dest_dir)
            assert received_name == expected_name
            with open(expected_name) as result_file:
                received_content = result_file.read().strip()
            assert received_content == expected_content


def test_exc_nodir_download():
    dest_dir = 'notadir'
    with pytest.raises(NotADirectoryError):
        download(source_url, dest_dir)


def mock_matcher(request):
    url = request.url
    mocked_urls = []
    # mocked_urls.append(source_url)
    for resource in resources:
        mocked_urls.append(resource['url'])
    return url in mocked_urls


def test_download_resources(requests_mock):
    to_download = {
        'testnetloc-com-pics-pic1.jpg': 'http://testnetloc.com/pics/pic1.jpg',
        'testnetloc-com-pics-pic2.png': 'pics/pic2.png',
    }
    requests_mock.get(
        req_mock.ANY,  # Mock any URL before matching
        additional_matcher=mock_matcher,  # Mock only matched
        text="Some fake response",
    )
    with tempfile.TemporaryDirectory() as tmpdirname:
        download_resources(to_download, domain, tmpdirname)
        for resource in to_download.keys():
            path = os.path.join(tmpdirname, resource)
            assert os.path.exists(path)
