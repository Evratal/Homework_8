from django.core.exceptions import ValidationError
from urllib.parse import urlparse

def validate_youtube_url(value):
    """Проверяет, что ссылка ведет на youtube.com"""
    if value:
        parsed_url = urlparse(value)
        if parsed_url.netloc not in ('youtube.com', 'www.youtube.com', 'm.youtube.com'):
            raise ValidationError('Разрешены только ссылки на youtube.com')
