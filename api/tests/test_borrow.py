import pytest
import json
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from api.models import Book, Member


@pytest.mark.django_db
class TestBookBorrow:
    """Test cases for book borrowing functionality."""

    def setup_method(self):
        """Set up test client, user, authentication, and test data."""
        self.client = APIClient()
        self.client.default_format = 'json'

        # Create admin user
        self.user = User.objects.create_superuser(
            username='testadmin',
            email='testadmin@example.com',
            password='testpass123'
        )

        # Get auth token
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        # Create test member
        self.member = Member.objects.create(
            name='John Doe',
            email='john@example.com',
            address='123 Main St',
            phone='555-1234'
        )

        # Create available book
        self.available_book = Book.objects.create(
            title='Available Book',
            author='Test Author',
            published_year=2023,
            status='available'
        )

        # Create already borrowed book
        self.borrowed_book = Book.objects.create(
            title='Borrowed Book',
            author='Test Author',
            published_year=2022,
            status='borrowed',
            borrower=self.member
        )

    def test_borrow_available_book(self):
        """Test successfully borrowing an available book."""
        response = self.client.post(
            f'/api/books/{self.available_book.id}/borrow/',
            {'member_id': self.member.id},
            format='json'
        )

        content = json.loads(response.content)

        assert response.status_code == 200
        assert 'code' in content
        assert 'status' in content
        assert 'data' in content
        assert content['code'] == 200
        assert content['status'] == 'OK'
        assert content['data']['status'] == 'borrowed'
        assert content['data']['borrower'] == self.member.id

        # Verify in database
        self.available_book.refresh_from_db()
        assert self.available_book.status == 'borrowed'
        assert self.available_book.borrower == self.member

    def test_borrow_already_borrowed_book(self):
        """Test error when trying to borrow an already borrowed book."""
        response = self.client.post(
            f'/api/books/{self.borrowed_book.id}/borrow/',
            {'member_id': self.member.id},
            format='json'
        )

        content = json.loads(response.content)

        assert response.status_code == 400
        assert content['code'] == 400
        assert 'error' in content['data']
        assert isinstance(content['data']['error'], list)
        assert len(content['data']['error']) > 0

    def test_borrow_book_missing_member_id(self):
        """Test error when member_id is not provided."""
        response = self.client.post(
            f'/api/books/{self.available_book.id}/borrow/',
            {},
            format='json'
        )

        content = json.loads(response.content)

        assert response.status_code == 400
        assert content['code'] == 400
        assert 'error' in content['data']

    def test_borrow_book_invalid_member_id(self):
        """Test error when member_id does not exist."""
        response = self.client.post(
            f'/api/books/{self.available_book.id}/borrow/',
            {'member_id': 99999},  # Non-existent member
            format='json'
        )

        content = json.loads(response.content)

        assert response.status_code == 400
        assert content['code'] == 400
        assert 'error' in content['data']

    def test_return_borrowed_book(self):
        """Test returning a borrowed book (bonus feature)."""
        # First ensure book is borrowed
        assert self.borrowed_book.status == 'borrowed'

        response = self.client.post(
            f'/api/books/{self.borrowed_book.id}/return_book/',
            format='json'
        )

        content = json.loads(response.content)

        assert response.status_code == 200
        assert content['code'] == 200
        assert content['data']['status'] == 'available'
        assert content['data']['borrower'] is None

        # Verify in database
        self.borrowed_book.refresh_from_db()
        assert self.borrowed_book.status == 'available'
        assert self.borrowed_book.borrower is None

    def test_return_available_book(self):
        """Test error when trying to return a book that's not borrowed."""
        response = self.client.post(
            f'/api/books/{self.available_book.id}/return_book/',
            format='json'
        )

        content = json.loads(response.content)

        assert response.status_code == 400
        assert content['code'] == 400
        assert 'error' in content['data']

    def test_borrow_book_unauthenticated(self):
        """Test that unauthenticated users cannot borrow books."""
        self.client.credentials()  # Remove authentication

        response = self.client.post(
            f'/api/books/{self.available_book.id}/borrow/',
            {'member_id': self.member.id},
            format='json'
        )

        content = json.loads(response.content)

        assert response.status_code == 401
        assert content['code'] == 401
        assert 'error' in content['data']
