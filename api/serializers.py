from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['id','first_name', 'last_name', 'username', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        # Normally you would need to handle the password confirmation separately,
        # but since it's removed, we expect that the frontend has handled this.
        user = User(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['username']
        )
        user.set_password(password)
        user.save()
        return user
