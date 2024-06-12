# serializers.py
from rest_framework import serializers
from userauths.models import Profile, User
from .models import Category, Lesson, Activity, Payment
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'username', 'phone']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            phone=validated_data['phone']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField()
    password = serializers.CharField()    

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'
        
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "image"]


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "title", "category", "lesson_type", "content", "image"]


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = [
            "id",
            "user",
            "lesson",
            "purchase_date",
            "image",
            "description",
            "activity_name",
        ]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "user", "reference", "activity", "amount", "date", "status"]
