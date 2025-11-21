from django.contrib.auth import authenticate
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework.authtoken.models import Token
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .models import Book, Member
from .serializers import BookSerializer, MemberSerializer


@extend_schema(
    tags=['Authentication'],
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string'},
                'password': {'type': 'string'}
            },
            'required': ['username', 'password']
        }
    },
    responses={
        200: {
            'type': 'object',
            'properties': {
                'code': {'type': 'integer'},
                'status': {'type': 'string'},
                'data': {
                    'type': 'object',
                    'properties': {
                        'token': {'type': 'string'}
                    }
                }
            }
        }
    },
    description='Administrator login endpoint. Returns authentication token.',
    summary='Login'
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Administrator login endpoint.

    Accepts username and password, returns authentication token.
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if not username:
        raise ValidationError({'username': ['This field is required.']})

    if not password:
        raise ValidationError({'password': ['This field is required.']})

    user = authenticate(username=username, password=password)

    if user is None:
        raise AuthenticationFailed('Invalid credentials.')

    # Get or create token for user
    token, created = Token.objects.get_or_create(user=user)

    return Response({
        'token': token.key
    }, status=status.HTTP_200_OK)


@extend_schema(tags=['Books'])
class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing books.

    Provides CRUD operations for books and borrowing functionality.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Allow filtering by status."""
        queryset = Book.objects.all()
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'member_id': {'type': 'integer'}
                },
                'required': ['member_id']
            }
        },
        responses={200: BookSerializer},
        description='Borrow a book for a member. The book must be available.',
        summary='Borrow a book'
    )
    @action(detail=True, methods=['post'])
    def borrow(self, request, pk=None):
        """
        Borrow a book for a member.

        Expects: {"member_id": <member_id>}
        """
        book = self.get_object()
        member_id = request.data.get('member_id')

        if not member_id:
            raise ValidationError({'member_id': ['This field is required.']})

        # Verify member exists
        try:
            member = Member.objects.get(id=member_id)
        except Member.DoesNotExist:
            raise ValidationError({'member_id': ['Member does not exist.']})

        # Check if book is available
        if book.status != 'available':
            raise ValidationError('This book is already borrowed.')

        # Update book status
        book.status = 'borrowed'
        book.borrower = member
        book.save()

        serializer = self.get_serializer(book)
        return Response(serializer.data)

    @extend_schema(
        responses={200: BookSerializer},
        description='Return a borrowed book. Makes the book available again.',
        summary='Return a book'
    )
    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        """
        Return a borrowed book.

        Makes the book available again and removes the borrower.
        """
        book = self.get_object()

        # Check if book is actually borrowed
        if book.status != 'borrowed':
            raise ValidationError('This book is not currently borrowed.')

        # Update book status
        book.status = 'available'
        book.borrower = None
        book.save()

        serializer = self.get_serializer(book)
        return Response(serializer.data)


@extend_schema(tags=['Members'])
class MemberViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing members.

    Provides CRUD operations for library members.
    """
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]


