import pytest
import json

from app import app

def test_home_page(client):
    response = client.get('/')
    assert b'URL to be shortened:' in response.data
    assert response.status_code == 200

@pytest.mark.parametrize(('url', 'success'), (
    ('', False),
    ('wrong://wrong.wrong', False),
    ('https://www.google.com', True)
))
def test_login_credentials(client, url, success):
    mock_data = {
        'url':url
    }
    response = client.post('/api/shorturl/new', data=mock_data, follow_redirects=True)
    if success:
        assert response.status_code == 201
        assert bytes(url, 'ascii') in response.data
    else:
        assert response.status_code == 400
        assert b'Invalid URL' in response.data
    return response

@pytest.mark.parametrize(('url', 'success'), (
    ('', False),
    ('https://www.google.com', True)
))
def test_get_all_url(client, url, success):
    response = client.get('/api/shorturl/')
    assert response.status_code == 200
    if success:
        assert bytes(url, 'ascii') in response.data

@pytest.mark.parametrize(('url', 'success'), (
    ('', False),
    ('https://www.google.com', True)
))
def test_get_url(client, url, success):
    post_url = '/api/shorturl/new'
    mock_data = {
        'url':url
    }
    response = client.post(post_url, data=mock_data)
    if response.status_code == 201:
        code = response.json['url']['shortened_url']
    else:
        code = 'randomcode'

    get_url = '/api/shorturl/' + str(code)
    response = client.get(get_url)
    if success:
        assert response.status_code == 200
        assert bytes(url, 'ascii') in response.data
        assert bytes(code, 'ascii') in response.data
    else:
        assert response.status_code == 404
        assert b'Not found' in response.data