# views.py
from rest_framework import generics, permissions, views
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from rest_framework import status, viewsets
from django.db.models import Count
from .serializers import UserRegistrationSerializer, ChatbotSerializer, PlaceSerializer, ProfileSerializer, LikePlaceSerializer, SubPlaceSerializer, ProfileSerializer
from .models import Places, LikePlace, SubPlaces, Profile
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
from django.views.decorators.csrf import csrf_exempt

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


class UserLikedPlacesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        liked_places = LikePlace.objects.filter(user_like_id=user_id)
        serializer = LikePlaceSerializer(liked_places, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class SubPlacesByPlaceView(APIView):
    def get(self, request, placeId, *args, **kwargs):
        try:
            # Filter SubPlaces by the given placeId
            subplaces = SubPlaces.objects.filter(place__id=placeId)
            
            # Serialize the data
            serializer = SubPlaceSerializer(subplaces, many=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Places.DoesNotExist:
            return Response({"error": "Place not found"}, status=status.HTTP_404_NOT_FOUND)




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
            # Check if '|' is in the answer and replace it with two <br> tags if present
            answer_with_line_breaks = q["answer"].replace('|', '<br><br>') if '|' in q["answer"] else q["answer"]
            return answer_with_line_breaks
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
        
        
        
        
class ApprovedPlaceListView(generics.ListAPIView):
    serializer_class = PlaceSerializer

    def get_queryset(self):
        # Filter places that are only 'Approved'
        return Places.objects.filter(status='Approved')

class OngoingPlaceListView(generics.ListAPIView):
    serializer_class = PlaceSerializer

    def get_queryset(self):
        # Filter places that are only 'On-going'
        return Places.objects.filter(status='On-going')
    



class UpdateBirthdayView(generics.GenericAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        try:
            # Fetch the user object first
            user = User.objects.get(id=user_id)
            profile, created = Profile.objects.get_or_create(user=user)  # Create profile if it doesn't exist
            
            # Update the birthday
            birthday = request.data.get('birthday')
            if birthday:
                profile.birthday = birthday
                profile.save()
                serializer = self.get_serializer(profile)
                return Response(serializer.data, status=status.HTTP_201_CREATED)  # Birthday created
            else:
                return Response({"detail": "Birthday not provided."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, user_id):
        try:
            # Fetch the user object first
            user = User.objects.get(id=user_id)
            profile = self.queryset.get(user=user)  # Fetch profile by user instance
            
            # Update the birthday
            birthday = request.data.get('birthday')
            if birthday:
                profile.birthday = birthday
                profile.save()
                serializer = self.get_serializer(profile)
                return Response(serializer.data)
            else:
                return Response({"detail": "Birthday not provided."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Profile.DoesNotExist:
            return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
        
# View to retrieve a user's birthday based on user ID
class UserBirthdayView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, user_id):
        # Get the profile associated with the user_id
        return get_object_or_404(Profile, user__id=user_id)

    def get(self, request, user_id):
        profile = self.get_object(user_id)
        serializer = self.get_serializer(profile)
        # Return only the birthday field
        return Response({"birthday": serializer.data.get("birthday")})
    


class UpdateProfileView(generics.UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, user_id):
        try:
            profile = self.queryset.get(user__id=user_id)  # Fetch profile by user ID
        except Profile.DoesNotExist:
            return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserProfilePictureView(APIView):
    def get(self, request, user_id):
        try:
            # Fetch the user's profile using the user ID
            profile = Profile.objects.get(user__id=user_id)
            # Return the profile picture URL or None if it doesn't exist
            profile_pic_url = profile.profile_pic.url if profile.profile_pic else None
            return Response({'profile_pic': profile_pic_url}, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)