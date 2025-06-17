from django.urls import path
from .views import delayed_response, get_version

urlpatterns = [
    path('response/', delayed_response, name='delayed_response'),  # 模拟延迟响应
    path('version/', get_version, name='get_version'),  # 直接返回版本号
]