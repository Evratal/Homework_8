from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("email", "is_staff")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            ("Personal info"),
            {"fields": ("first_name", "last_name", "phone", "city", "avatar")},
        ),
        (("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser")}),
        (("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    ordering = ("email",)
