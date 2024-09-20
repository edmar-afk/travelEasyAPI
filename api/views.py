# views.py
from rest_framework import generics, permissions, views
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from rest_framework import status, viewsets
from django.db.models import Count
from .serializers import UserRegistrationSerializer, ChatbotSerializer, PlaceSerializer, LikePlaceSerializer
from .models import Places, LikePlace
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.views import View
from rest_framework.decorators import api_view, permission_classes
import json
from difflib import get_close_matches
from django.conf import settings
import os
BASE_DIR = settings.BASE_DIR

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated access
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    


class PlaceListView(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated access
    def get(self, request):
        places = Places.objects.all()
        serializer = PlaceSerializer(places, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PlaceDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]  # Allow unauthenticated access
    queryset = Places.objects.all()
    serializer_class = PlaceSerializer
    lookup_field = 'id'
    
class LikePlaceView(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated access
    def post(self, request, place_id):
        user = request.user
        try:
            place = Places.objects.get(id=place_id)
        except Places.DoesNotExist:
            return Response({"error": "Place not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the user has already liked this place
        if LikePlace.objects.filter(user_like=user, place_name=place).exists():
            return Response({"error": "You have already liked this place."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create a new LikePlace instance
        like_place = LikePlace(user_like=user, place_name=place)
        like_place.save()
        
        serializer = LikePlaceSerializer(like_place)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([AllowAny])  # Allow anyone to access this view
def check_place_liked(request, placeid):
    if request.user.is_authenticated:
        liked = LikePlace.objects.filter(user_like=request.user, place_name_id=placeid).exists()
        return Response({'liked': liked})
    return Response({'liked': False})  # Default response for unauthenticated users

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Only authenticated users can dislike a place
def dislike_place(request, placeid):
    user = request.user
    try:
        like = LikePlace.objects.get(user_like=user, place_name_id=placeid)
        like.delete()
        return Response({'message': 'Disliked the place successfully'})
    except LikePlace.DoesNotExist:
        return Response({'message': 'Like entry does not exist'}, status=404)


class DisplayLikesView(generics.GenericAPIView):
    permission_classes = [AllowAny]  # Allow unauthenticated access
    def get(self, request, *args, **kwargs):
        place_id = self.kwargs.get('place_id')
        if place_id is not None:
            count = LikePlace.objects.filter(place_name_id=place_id).count()
            return Response({'like_count': count})
        return Response({'error': 'Place ID not provided'}, status=400)


class PlaceListView(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated access
    def get(self, request, *args, **kwargs):
        # Get all places and annotate them with the count of likes
        places = Places.objects.annotate(like_count=Count('likeplace')).order_by('-like_count')
        
        # Serialize the data
        serializer = PlaceSerializer(places, many=True)
        
        return Response(serializer.data)





    
# Load the knowledge base from a JSON file
def load_knowledge_base(file_path: str):
    full_path = os.path.join(BASE_DIR, file_path)
    with open(full_path, 'r') as file:
        data = json.load(file)
    return data

# Save the updated knowledge base to the JSON file
def save_knowledge_base(file_path: str, data: dict):
    full_path = os.path.join(BASE_DIR, file_path)
    with open(full_path, 'w') as file:
        json.dump(data, file, indent=2)


def find_best_match(user_question: str, questions: list[str]) -> str | None:
    matches = get_close_matches(user_question, questions, n=1, cutoff=0.6)
    return matches[0] if matches else None

def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
    for q in knowledge_base["questions"]:
        if q["question"] == question:
            return q["answer"]
    return None
class ChatbotViewSet(viewsets.ViewSet):
    serializer_class = ChatbotSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user_question = serializer.validated_data['question']
            knowledge_base = load_knowledge_base('knowledge_base.json')
            best_match = find_best_match(user_question, [q["question"] for q in knowledge_base["questions"]])

            if best_match:
                answer = get_answer_for_question(best_match, knowledge_base)
                return Response({'answer': answer}, status=status.HTTP_200_OK)
            else:
                return Response({'answer': "I don't understand the question."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)