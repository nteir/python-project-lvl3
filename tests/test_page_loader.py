from page_loader.page_loader import download
import os.path
from unittest.mock import patch, MagicMock


@patch('urllib.request.urlopen')
def test_request_download(mock_urlopen):
    source_url = 'http://dkfgjrdirjwsopiej.com/host/fake_test.html'
    dest_dir = './tests/fixtures/'
    expected_content = 'sample text'
    expected_name = os.path.join(dest_dir, 'dkfgjrdirjwsopiej-com-host-fake_test.html')
    mock = MagicMock()
    mock.getcode.return_value = 200
    mock.__enter__.return_value = mock
    mock.read.return_value = expected_content.encode('utf-8')
    mock_urlopen.return_value = mock
    received_name = download(source_url, dest_dir)
    assert received_name == expected_name
    with open(expected_name) as result_file:
        received_content = result_file.read()
    assert received_content == expected_content
