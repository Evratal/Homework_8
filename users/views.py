from drf_yasg import openapi
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
import django_filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Subscription
from course.models import Course
from drf_yasg.utils import swagger_auto_schema
from django.urls import reverse
from users.service import (
    create_stripe_product,
    create_stripe_price,
    create_stripe_session
)


from .models import User, Payment
from .serializers import (
    UserSerializer,
    PaymentSerializer,
    MyTokenObtainPairSerializer,
    UserRegisterSerializer,
    UserProfileSerializer,
    UserDetailSerializer,
)

class PaymentFilter(django_filters.FilterSet):
    course = django_filters.NumberFilter(field_name="paid_course__id")
    lesson = django_filters.NumberFilter(field_name="paid_lesson__id")
    method = django_filters.ChoiceFilter(choices=Payment.PAYMENT_METHODS)
    min_amount = django_filters.NumberFilter(field_name="amount", lookup_expr="gte")
    max_amount = django_filters.NumberFilter(field_name="amount", lookup_expr="lte")

    class Meta:
        model = Payment
        fields = []

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ["payment_date", "amount"]
    ordering = ["-payment_date"]

    def get_queryset(self):
        queryset = Payment.objects.select_related("user", "paid_course", "paid_lesson")
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Создаем продукт в Stripe
        course = serializer.validated_data.get('paid_course')
        lesson = serializer.validated_data.get('paid_lesson')

        product_name = course.title if course else lesson.title
        product = create_stripe_product(product_name)

        # Создаем цену в Stripe
        price = create_stripe_price(
            amount=serializer.validated_data['amount'],
            product_id=product.id
        )

        # Создаем сессию оплаты
        success_url = request.build_absolute_uri(reverse('payment-success'))
        cancel_url = request.build_absolute_uri(reverse('payment-cancel'))
        session = create_stripe_session(price.id, success_url, cancel_url)

        # Сохраняем платеж с ссылкой и ID сессии
        serializer.save(
            user=request.user,
            payment_link=session.url,
            stripe_session_id=session.id
        )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class PaymentSuccessView(APIView):
    """Обработчик успешной оплаты"""
    def get(self, request):
        return Response(
            {"status": "Payment successful"},
            status=status.HTTP_200_OK
        )

class PaymentCancelView(APIView):
    """Обработчик отмены оплаты"""
    def get(self, request):
        return Response(
            {"status": "Payment cancelled"},
            status=status.HTTP_200_OK
        )

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class UserListView(generics.ListAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()

class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()


class SubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(                                       #пример описания эндпоинтов
        operation_description="Подписка/отписка на курс",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'course_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID курса'),
            },
            required=['course_id']
        ),
        responses={
            200: openapi.Response(
                description="Успешная операция",
                examples={
                    "application/json": {
                        "message": "Подписка добавлена"
                    }
                }
            )
        }
    )

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course_id')
        course = get_object_or_404(Course, id=course_id)

        subscription, created = Subscription.objects.get_or_create(
            user=user,
            course=course
        )

        if not created:
            subscription.delete()
            message = 'Подписка удалена'
        else:
            message = 'Подписка добавлена'

        return Response({"message": message}, status=status.HTTP_200_OK)
