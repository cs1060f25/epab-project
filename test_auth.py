"""Basic unit tests for Auth0 authentication"""

import pytest
from unittest.mock import Mock, patch
from server import app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_home_route_without_session(client):
    """Test that home page loads without authentication"""
    response = client.get('/')
    assert response.status_code == 200


def test_home_route_with_session(client):
    """Test that home page loads with user session"""
    with client.session_transaction() as sess:
        sess['user'] = {'name': 'Test User', 'email': 'test@example.com'}

    response = client.get('/')
    assert response.status_code == 200


@patch('server.oauth.auth0.authorize_redirect')
def test_login_route(mock_authorize, client):
    """Test that login route initiates OAuth redirect"""
    mock_authorize.return_value = Mock(status_code=302)

    response = client.get('/login')

    # Verify that authorize_redirect was called
    mock_authorize.assert_called_once()


def test_logout_route_clears_session(client):
    """Test that logout route clears session and redirects"""
    # Set up a session
    with client.session_transaction() as sess:
        sess['user'] = {'name': 'Test User', 'email': 'test@example.com'}

    response = client.get('/logout', follow_redirects=False)

    # Should redirect to Auth0 logout
    assert response.status_code == 302
    assert 'auth0.com' in response.location

    # Check that session would be cleared (session is cleared during the request)
    with client.session_transaction() as sess:
        assert 'user' not in sess


@patch('server.oauth.auth0.authorize_access_token')
def test_callback_route(mock_token, client):
    """Test that callback route handles OAuth token and sets session"""
    mock_token.return_value = {
        'access_token': 'test_token',
        'userinfo': {
            'name': 'Test User',
            'email': 'test@example.com'
        }
    }

    response = client.get('/callback', follow_redirects=False)

    # Should redirect to home
    assert response.status_code == 302
    assert response.location == '/'

    # Verify token was retrieved
    mock_token.assert_called_once()
