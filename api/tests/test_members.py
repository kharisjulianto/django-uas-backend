import pytest
import json
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from api.models import Member


@pytest.mark.django_db
class TestMemberCRUD:
    """Test cases for member CRUD operations."""

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

    def test_create_member(self):
        """Test creating a new member."""
        response = self.client.post('/api/members/', {
            'name': 'John Doe',
            'email': 'john@example.com',
            'address': '123 Main St',
            'phone': '555-1234'
        }, format='json')

        content = json.loads(response.content)

        assert response.status_code == 201
        assert 'code' in content
        assert 'status' in content
        assert 'data' in content
        assert content['code'] == 201
        assert content['status'] == 'CREATED'
        assert content['data']['name'] == 'John Doe'
        assert content['data']['email'] == 'john@example.com'
        assert content['data']['address'] == '123 Main St'
        assert content['data']['phone'] == '555-1234'
        assert 'id' in content['data']
        assert 'join_date' in content['data']

    def test_list_members(self):
        """Test listing all members."""
        # Create test members
        Member.objects.create(
            name='Member 1',
            email='member1@example.com',
            address='Address 1',
            phone='111-1111'
        )
        Member.objects.create(
            name='Member 2',
            email='member2@example.com',
            address='Address 2',
            phone='222-2222'
        )

        response = self.client.get('/api/members/', format='json')
        content = json.loads(response.content)

        assert response.status_code == 200
        assert 'code' in content
        assert 'data' in content
        assert content['code'] == 200
        assert isinstance(content['data'], list)
        assert len(content['data']) >= 2

    def test_retrieve_member(self):
        """Test retrieving a specific member."""
        member = Member.objects.create(
            name='Test Member',
            email='test@example.com',
            address='Test Address',
            phone='555-0000'
        )

        response = self.client.get(f'/api/members/{member.id}/', format='json')
        content = json.loads(response.content)

        assert response.status_code == 200
        assert content['code'] == 200
        assert content['data']['id'] == member.id
        assert content['data']['name'] == 'Test Member'
        assert content['data']['email'] == 'test@example.com'

    def test_update_member(self):
        """Test updating a member."""
        member = Member.objects.create(
            name='Original Name',
            email='original@example.com',
            address='Original Address',
            phone='111-1111'
        )

        response = self.client.put(f'/api/members/{member.id}/', {
            'name': 'Updated Name',
            'email': 'updated@example.com',
            'address': 'Updated Address',
            'phone': '222-2222'
        }, format='json')

        content = json.loads(response.content)

        assert response.status_code == 200
        assert content['code'] == 200
        assert content['data']['name'] == 'Updated Name'
        assert content['data']['email'] == 'updated@example.com'
        assert content['data']['address'] == 'Updated Address'
        assert content['data']['phone'] == '222-2222'

    def test_partial_update_member(self):
        """Test partially updating a member."""
        member = Member.objects.create(
            name='Original Name',
            email='original@example.com',
            address='Original Address',
            phone='111-1111'
        )

        response = self.client.patch(f'/api/members/{member.id}/', {
            'phone': '999-9999'
        }, format='json')

        content = json.loads(response.content)

        assert response.status_code == 200
        assert content['code'] == 200
        assert content['data']['phone'] == '999-9999'
        assert content['data']['name'] == 'Original Name'  # Unchanged
        assert content['data']['email'] == 'original@example.com'  # Unchanged

    def test_delete_member(self):
        """Test deleting a member."""
        member = Member.objects.create(
            name='To Be Deleted',
            email='delete@example.com',
            address='Delete Address',
            phone='000-0000'
        )

        response = self.client.delete(f'/api/members/{member.id}/', format='json')

        assert response.status_code == 204
        assert not Member.objects.filter(id=member.id).exists()

    def test_create_member_unauthenticated(self):
        """Test that unauthenticated users cannot create members."""
        self.client.credentials()  # Remove authentication

        response = self.client.post('/api/members/', {
            'name': 'Test Member',
            'email': 'test@example.com',
            'address': 'Test Address',
            'phone': '555-0000'
        }, format='json')

        content = json.loads(response.content)

        assert response.status_code == 401
        assert content['code'] == 401
        assert 'error' in content['data']

    def test_create_member_missing_required_field(self):
        """Test validation error for missing required field."""
        response = self.client.post('/api/members/', {
            'email': 'test@example.com',
            'address': 'Test Address',
            'phone': '555-0000'
            # Missing 'name'
        }, format='json')

        content = json.loads(response.content)

        assert response.status_code == 400
        assert content['code'] == 400
        assert 'error' in content['data']
        assert isinstance(content['data']['error'], list)

    def test_create_member_duplicate_email(self):
        """Test validation error for duplicate email."""
        # Create first member
        Member.objects.create(
            name='First Member',
            email='duplicate@example.com',
            address='Address 1',
            phone='111-1111'
        )

        # Try to create second member with same email
        response = self.client.post('/api/members/', {
            'name': 'Second Member',
            'email': 'duplicate@example.com',
            'address': 'Address 2',
            'phone': '222-2222'
        }, format='json')

        content = json.loads(response.content)

        assert response.status_code == 400
        assert content['code'] == 400
        assert 'error' in content['data']
