from page_loader.page_loader import download, download_resources, process_html
import os.path
import tempfile
import requests_mock as req_mock
import pytest

source_url = 'http://testnetloc.com/some/path/fake_test.html'
file_name = 'testnetloc-com-some-path-fake_test.html'
resource_dir = 'testnetloc-com-some-path-fake_test_files'
domain = 'testnetloc.com'
with open('./tests/fixtures/fake_test.html') as file:
    content = file.read()
resources = [
    {
        'url': 'http://testnetloc.com/pics/pic1.jpg',
        'expected_name': 'testnetloc-com-pics-pic1.jpg'
    },
    {
        'url': 'http://testnetloc.com/pics/pic2.png',
        'expected_name': 'testnetloc-com-pics-pic2.png'
    },
    {
        'url': 'http://testnetloc.com/style/style.css',
        'expected_name': 'testnetloc-com-style-style.css'
    },
]
to_download = {
    'testnetloc-com-pics-pic1.jpg': 'http://testnetloc.com/pics/pic1.jpg',
    'testnetloc-com-pics-pic2.png': '/pics/pic2.png',
    'testnetloc-com-style-style.css': '/style/style.css',
}


def test_request_download(requests_mock):
    expected_content = 'sample text'
    requests_mock.get(source_url, text=expected_content)
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
    for resource in resources:
        mocked_urls.append(resource['url'])
    return url in mocked_urls


def test_download_resources(requests_mock):
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


def test_process_html():
    output, res_dict = process_html(content, domain, resource_dir)
    with open('./tests/fixtures/expected.html') as file:
        expected_content = file.read()
    assert res_dict == to_download
    assert output == expected_content
