from rest_framework import serializers
from .models import Payment, User
from course.serializers import CourseSerializer, LessonSerializer

class PaymentSerializer(serializers.ModelSerializer):
    # Сериализаторы для связанных полей
    paid_course = CourseSerializer(read_only=True)
    paid_lesson = LessonSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'payment_date',
            'paid_course', 'paid_lesson',
            'amount', 'payment_method'
        ]


class UserSerializer(serializers.ModelSerializer):
    payments = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar', 'payments']

    def get_payments(self, instance):
        payments = instance.payments.all().order_by('-payment_date')
        return PaymentSerializer(payments, many=True).data