import pytest
import json
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from api.models import Book, Member


@pytest.mark.django_db
class TestBookCRUD:
    """Test cases for book CRUD operations."""

    def setup_method(self):
        """Set up test client, user, and authentication."""
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

        # Create a member for borrowing tests
        self.member = Member.objects.create(
            name='John Doe',
            email='john@example.com',
            address='123 Main St',
            phone='555-1234',
        )

    def test_create_book(self):
        """Test creating a new book."""
        response = self.client.post('/api/books/', {
            'title': 'Test Book',
            'author': 'Test Author',
            'published_year': 2023,
            'status': 'available'
        }, format='json')

        content = json.loads(response.content)

        assert response.status_code == 201
        assert 'code' in content
        assert 'status' in content
        assert 'data' in content
        assert content['code'] == 201
        assert content['status'] == 'CREATED'
        assert content['data']['title'] == 'Test Book'
        assert content['data']['author'] == 'Test Author'
        assert content['data']['published_year'] == 2023
        assert content['data']['status'] == 'available'
        assert 'id' in content['data']

    def test_list_books(self):
        """Test listing all books."""
        # Create test books
        Book.objects.create(
            title='Book 1',
            author='Author 1',
            published_year=2020,
            status='available'
        )
        Book.objects.create(
            title='Book 2',
            author='Author 2',
            published_year=2021,
            status='borrowed',
            borrower=self.member
        )

        response = self.client.get('/api/books/', format='json')
        content = json.loads(response.content)

        assert response.status_code == 200
        assert 'code' in content
        assert 'data' in content
        assert content['code'] == 200
        assert isinstance(content['data'], list)
        assert len(content['data']) >= 2

    def test_retrieve_book(self):
        """Test retrieving a specific book."""
        book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            published_year=2023,
            status='available'
        )

        response = self.client.get(f'/api/books/{book.id}/', format='json')
        content = json.loads(response.content)

        assert response.status_code == 200
        assert content['code'] == 200
        assert content['data']['id'] == book.id
        assert content['data']['title'] == 'Test Book'

    def test_update_book(self):
        """Test updating a book."""
        book = Book.objects.create(
            title='Original Title',
            author='Original Author',
            published_year=2020,
            status='available'
        )

        response = self.client.put(f'/api/books/{book.id}/', {
            'title': 'Updated Title',
            'author': 'Updated Author',
            'published_year': 2021,
            'status': 'available'
        }, format='json')

        content = json.loads(response.content)

        assert response.status_code == 200
        assert content['code'] == 200
        assert content['data']['title'] == 'Updated Title'
        assert content['data']['author'] == 'Updated Author'
        assert content['data']['published_year'] == 2021

    def test_partial_update_book(self):
        """Test partially updating a book."""
        book = Book.objects.create(
            title='Original Title',
            author='Original Author',
            published_year=2020,
            status='available'
        )

        response = self.client.patch(f'/api/books/{book.id}/', {
            'title': 'Patched Title'
        }, format='json')

        content = json.loads(response.content)

        assert response.status_code == 200
        assert content['code'] == 200
        assert content['data']['title'] == 'Patched Title'
        assert content['data']['author'] == 'Original Author'  # Unchanged

    def test_delete_book(self):
        """Test deleting a book."""
        book = Book.objects.create(
            title='To Be Deleted',
            author='Test Author',
            published_year=2020,
            status='available'
        )

        response = self.client.delete(f'/api/books/{book.id}/', format='json')

        assert response.status_code == 204
        assert not Book.objects.filter(id=book.id).exists()

    def test_create_book_unauthenticated(self):
        """Test that unauthenticated users cannot create books."""
        self.client.credentials()  # Remove authentication

        response = self.client.post('/api/books/', {
            'title': 'Test Book',
            'author': 'Test Author',
            'published_year': 2023,
            'status': 'available'
        }, format='json')

        content = json.loads(response.content)

        assert response.status_code == 401
        assert content['code'] == 401
        assert 'error' in content['data']

    def test_create_book_missing_required_field(self):
        """Test validation error for missing required field."""
        response = self.client.post('/api/books/', {
            'author': 'Test Author',
            'published_year': 2023,
            'status': 'available'
            # Missing 'title'
        }, format='json')

        content = json.loads(response.content)

        assert response.status_code == 400
        assert content['code'] == 400
        assert 'error' in content['data']
        assert isinstance(content['data']['error'], list)
