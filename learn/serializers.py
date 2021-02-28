from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Course, Lesson
from main.models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['bio', 'image', 'mataz']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(many=False)
    class Meta:
        model = get_user_model()
        fields = ['username', 'first_name', 'last_name', 'profile']

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['title', 'description', 'youtube']

class CourseSerializer(serializers.ModelSerializer):
    owner = UserSerializer(many=False)
    lessons = LessonSerializer(many=True)

    class Meta:
        model = Course
        fields = ['title', 'owner', 'short_description',
                  'description', 'predecessor', 'youtube', 'lessons'
                  ]
