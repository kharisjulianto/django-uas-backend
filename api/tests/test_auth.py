import pytest
import json
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token


@pytest.mark.django_db
class TestAuthentication:
    """Test cases for administrator authentication."""

    def setup_method(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.client.default_format = 'json'
        self.username = 'testadmin'
        self.password = 'testpass123'
        self.user = User.objects.create_superuser(
            username=self.username,
            email='testadmin@example.com',
            password=self.password
        )

    def test_successful_login(self):
        """Test successful login returns token in standardized format."""
        response = self.client.post('/api/auth/login/', {
            'username': self.username,
            'password': self.password
        }, format='json')

        # Parse the rendered content to verify the wrapper
        content = json.loads(response.content)

        assert response.status_code == 200
        assert 'code' in content
        assert 'status' in content
        assert 'data' in content
        assert content['code'] == 200
        assert content['status'] == 'OK'
        assert 'token' in content['data']

        # Verify token is valid
        token_key = content['data']['token']
        assert Token.objects.filter(key=token_key).exists()

    def test_failed_login_invalid_credentials(self):
        """Test failed login returns error in standardized format."""
        response = self.client.post('/api/auth/login/', {
            'username': self.username,
            'password': 'wrongpassword'
        }, format='json')

        content = json.loads(response.content)

        assert response.status_code == 401
        assert 'code' in content
        assert 'status' in content
        assert 'data' in content
        assert content['code'] == 401
        assert 'error' in content['data']
        assert isinstance(content['data']['error'], list)
        assert len(content['data']['error']) > 0

    def test_failed_login_missing_username(self):
        """Test login with missing username returns validation error."""
        response = self.client.post('/api/auth/login/', {
            'password': self.password
        }, format='json')

        content = json.loads(response.content)

        assert response.status_code == 400
        assert 'code' in content
        assert 'data' in content
        assert 'error' in content['data']

    def test_failed_login_missing_password(self):
        """Test login with missing password returns validation error."""
        response = self.client.post('/api/auth/login/', {
            'username': self.username
        }, format='json')

        content = json.loads(response.content)

        assert response.status_code == 400
        assert 'code' in content
        assert 'data' in content
        assert 'error' in content['data']

