from django.urls import path, include

from .views import TodoViewSet, UserCreate, UserLogin, UserLogout, UserView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'todos', TodoViewSet, basename='todo') # r means 'interpret the line literally, do not consider any escape characters'

urlpatterns = [
    path('', include(router.urls)),
    path('register', UserCreate.as_view(), name='register'),
    path('login', UserLogin.as_view(), name='login'),
    path('logout', UserLogout.as_view(), name='logout'),
    path('user', UserView.as_view(), name='user'),
    #path('', include('rest_framework.urls')),
]
