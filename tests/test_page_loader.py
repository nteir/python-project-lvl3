from page_loader.page_loader import download
import os.path
import tempfile
import requests_mock
import pytest


def test_request_download():
    source_url = 'http://dkfgjrdirjwsopiej.com/host/fake_test.html'
    expected_content = 'sample text'
    with requests_mock.Mocker() as mock:
        mock.get(source_url, text=expected_content)
        with tempfile.TemporaryDirectory() as tmpdirname:
            dest_dir = tmpdirname
            expected_name = os.path.join(dest_dir, 'dkfgjrdirjwsopiej-com-host-fake_test.html')
            received_name = download(source_url, dest_dir)
            assert received_name == expected_name
            with open(expected_name) as result_file:
                received_content = result_file.read()
            assert received_content == expected_content


def test_exc_nodir_download():
    source_url = 'http://dkfgjrdirjwsopiej.com/host/fake_test.html'
    dest_dir = 'notadir'
    with pytest.raises(NotADirectoryError):
        download(source_url, dest_dir)
