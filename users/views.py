from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import User, Payment
from .serializers import UserSerializer, PaymentSerializer
import django_filters

class PaymentFilter(django_filters.FilterSet):
    course = django_filters.NumberFilter(field_name='paid_course__id')
    lesson = django_filters.NumberFilter(field_name='paid_lesson__id')
    method = django_filters.ChoiceFilter(
        field_name='payment_method',
        choices=Payment.PAYMENT_METHOD_CHOICES
    )

    class Meta:
        model = Payment
        fields = ['course', 'lesson', 'method']

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ['payment_date', 'amount']
    ordering = ['-payment_date']