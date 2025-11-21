from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'books', views.BookViewSet, basename='book')
router.register(r'members', views.MemberViewSet, basename='member')

urlpatterns = [
    path('auth/login/', views.login, name='login'),
    path('', include(router.urls)),
]
