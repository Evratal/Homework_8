from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    PaymentViewSet,
    MyTokenObtainPairView,
    UserRegisterView,
    UserProfileView,
    UserListView,
    UserDetailView, SubscriptionAPIView, PaymentSuccessView, PaymentCancelView,
)

app_name = 'users'

router = DefaultRouter()
router.register(r"payments", PaymentViewSet, basename="payment")

urlpatterns = [
    path('subscriptions/', SubscriptionAPIView.as_view(), name='subscriptions'),
    path("auth/", include([
        path("login/", MyTokenObtainPairView.as_view(), name="login"),
        path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    ])),
    path("register/", UserRegisterView.as_view(), name="register"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("users/", include([
        path("", UserListView.as_view(), name="user-list"),
        path("<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    ])),
    path("", include(router.urls)),
    path('payment/success/', PaymentSuccessView.as_view(), name='payment-success'),
    path('payment/cancel/', PaymentCancelView.as_view(), name='payment-cancel'),
]
