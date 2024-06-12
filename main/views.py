# views.py
import uuid
import requests
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from userauths.models import Profile
from .models import User, Category, Lesson, Activity, Payment
from .serializers import (
    ProfileSerializer,
    UserLoginSerializer,
    UserRegistrationSerializer,
    CategorySerializer,
    LessonSerializer,
    ActivitySerializer,
    PaymentSerializer,
)
from django.contrib.auth import get_user_model, authenticate
from django.conf import settings
from rest_framework.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import AuthenticationFailed
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

    @swagger_auto_schema(
        method="post",
        request_body=UserRegistrationSerializer,
        responses={201: "User created"},
    )
    @action(detail=False, methods=["POST"], permission_classes=[AllowAny])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        username = serializer.validated_data.get("username")
        password = serializer.validated_data.get("password")

        if User.objects.filter(email=email).exists():
            raise ValidationError({"email": "Email already registered"})

        if User.objects.filter(username=username).exists():
            raise ValidationError({"username": "Username already registered"})

        try:
            validate_password(password)
        except ValidationError as e:
            raise ValidationError({"password": e.messages})

        user = serializer.save()
        return Response(
            {"status": "User created", "user": serializer.data},
            status=status.HTTP_201_CREATED,
        )

    @swagger_auto_schema(
        method="post",
        request_body=UserLoginSerializer,
        responses={200: "User authenticated"},
    )
    @action(detail=False, methods=["POST"], permission_classes=[AllowAny])
    def login(self, request):
        email_or_phone = request.data.get("email_or_phone")
        password = request.data.get("password")

        if not email_or_phone or not password:
            raise ValidationError({"detail": "Email/Phone and password are required"})

        user = None
        if "@" in email_or_phone:
            user = authenticate(request, username=email_or_phone, password=password)
        else:
            user = User.objects.filter(phone=email_or_phone).first()
            if user and user.check_password(password):
                user = authenticate(request, username=user.email, password=password)

        if not user:
            return Response(
                {"detail": "Invalid email/phone and password combination"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )

    @swagger_auto_schema(
        method="post",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "refresh": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Refresh token"
                )
            },
        ),
        responses={205: "Logged out"},
    )
    @action(detail=False, methods=["POST"], permission_classes=[IsAuthenticated])
    def logout(self, request):
        refresh_token = request.data.get("refresh")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        else:
            return Response(
                {"detail": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=["GET"], permission_classes=[IsAuthenticated])
    def list_users(self, request):
        users = self.queryset
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        user = self.get_object()
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @swagger_auto_schema(
        method='get',
        responses={200: 'List of paid activities'}
    )
    @action(detail=True, methods=["GET"], permission_classes=[IsAuthenticated])
    def paid_activities(self, request, pk=None):
        user = self.get_object()
        payments = Payment.objects.filter(user=user)
        paid_activities = [payment.activity for payment in payments]
        serializer = ActivitySerializer(paid_activities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["GET"])
    def verify_payment(self, request, pk=None):
        payment = self.get_object()
        paystack_url = f"https://api.paystack.co/transaction/verify/{payment.reference}"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        }

        response = requests.get(paystack_url, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            if response_data["data"]["status"] == "success":
                payment.status = "success"
                payment.save()

                lesson_type = payment.lesson.lesson_type
                if lesson_type == "video":
                    payment.user.videos_purchased += 1
                elif lesson_type == "worksheet":
                    payment.user.worksheets_purchased += 1
                elif lesson_type == "ebook":
                    payment.user.ebooks_purchased += 1
                payment.user.save()

                return Response(
                    {"message": "Payment verified and activity created"},
                    status=status.HTTP_200_OK,
                )
            else:
                payment.status = "failed"
                payment.save()
                return Response(
                    {"error": "Payment verification failed"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"error": "Payment verification failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @action(detail=False, methods=["POST"])
    def purchase_activity(self, request):
        user = request.user
        lesson_id = request.data.get("lesson_id")
        amount = request.data.get("amount")
        cover_image = request.data.get("cover_image")
        description = request.data.get("description")
        activity_name = request.data.get("activity_name")

        if not lesson_id or not amount:
            return Response(
                {"error": "Lesson ID and amount are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        lesson = Lesson.objects.get(id=lesson_id)

        reference = self.generate_reference()
        payment = Payment.objects.create(
            user=user, reference=reference, amount=amount, status="pending"
        )

        paystack_url = "https://api.paystack.co/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "email": user.email,
            "amount": int(amount) * 100,
            "reference": reference,
        }

        response = requests.post(paystack_url, json=data, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            payment.status = "initialized"
            payment.save()

            # Create activity record
            Activity.objects.create(
                user=user,
                lesson=lesson,
                cover_image=cover_image,
                description=description,
                activity_name=activity_name,
            )

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Payment initialization failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def generate_reference(self):
        return str(uuid.uuid4())

    @action(detail=True, methods=["POST"])
    def verify_payment(self, request, pk=None):
        payment = Payment.objects.get(id=pk)
        paystack_url = f"https://api.paystack.co/transaction/verify/{payment.reference}"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        }

        response = requests.get(paystack_url, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            if response_data["data"]["status"] == "success":
                payment.status = "success"
                payment.save()

                lesson_type = payment.lesson.lesson_type
                if lesson_type == "video":
                    payment.user.videos_purchased += 1
                elif lesson_type == "worksheet":
                    payment.user.worksheets_purchased += 1
                elif lesson_type == "ebook":
                    payment.user.ebooks_purchased += 1
                payment.user.save()

                return Response(
                    {"message": "Payment verified and activity created"},
                    status=status.HTTP_200_OK,
                )
            else:
                payment.status = "failed"
                payment.save()
                return Response(
                    {"error": "Payment verification failed"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"error": "Payment verification failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )
