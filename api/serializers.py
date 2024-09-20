from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Places, SubPlaces, LikePlace

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

class PlaceSerializer(serializers.ModelSerializer):
    like_count = serializers.SerializerMethodField()

    class Meta:
        model = Places
        fields = ['id', 'name', 'image', 'description', 'type', 'address', 'like_count']

    def get_like_count(self, obj):
        return LikePlace.objects.filter(place_name=obj).count()
        
class SubPlaceSerializer(serializers.ModelSerializer):
    place = PlaceSerializer()
    
    class Meta:
        model = SubPlaces
        fields = ['id', 'place', 'name', 'description', 'image', 'type']


class LikePlaceSerializer(serializers.ModelSerializer):
    place_name = PlaceSerializer()

    class Meta:
        model = LikePlace
        fields = ['id', 'user_like', 'place_name']
    
    







class ChatbotSerializer(serializers.Serializer):
    question = serializers.CharField()