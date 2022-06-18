from page_loader.page_loader import download


def test_download():
    download('a', 'b')
    assert True
