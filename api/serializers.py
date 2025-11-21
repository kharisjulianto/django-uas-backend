from rest_framework import serializers
from .models import Book, Member


class BookSerializer(serializers.ModelSerializer):
    """
    Serializer for Book model.

    Handles serialization and validation for book data.
    """

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'published_year', 'status', 'borrower']
        read_only_fields = ['id']

    def validate_status(self, value):
        """Validate book status is one of the allowed values."""
        valid_statuses = ['available', 'borrowed']
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        return value


class MemberSerializer(serializers.ModelSerializer):
    """
    Serializer for Member model.

    Handles serialization and validation for library member data.
    """

    class Meta:
        model = Member
        fields = ['id', 'name', 'email', 'address', 'phone', 'join_date']
        read_only_fields = ['id', 'join_date']

    def validate_email(self, value):
        """Validate email is unique across all members."""
        if self.instance is None:  # Create operation
            if Member.objects.filter(email=value).exists():
                raise serializers.ValidationError("A member with this email already exists.")
        else:  # Update operation
            if Member.objects.filter(email=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("A member with this email already exists.")
        return value
