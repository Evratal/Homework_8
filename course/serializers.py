from rest_framework import serializers
from .models import Course, Lesson
from .validators import validate_youtube_url


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"
        extra_kwargs = {
            'video_link': {'validators': [validate_youtube_url]}
        }

class CourseSerializer(serializers.ModelSerializer):

    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "preview",
            "description",
            "created_at",
            "updated_at",
            "lessons",
            "lessons_count",
            "is_subscribed",
        ]

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.subscriptions.filter(user=user).exists()
        return False
