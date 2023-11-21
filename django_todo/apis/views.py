from django.contrib.auth.models import User
from rest_framework import viewsets, views, status, serializers
from drf_spectacular.utils import extend_schema, inline_serializer
from drf_spectacular.types import OpenApiTypes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from django.contrib.auth import login, logout
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action

from todos import models
from .serializers import TodoSerializer, UserLoginSerializer, UserSerializer
from .permissions import IsOwnerOrReadOnly
from .filters import TodoFilter
from .pagination import CustomPageNumberPagination


class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = CustomPageNumberPagination
    pagination_class.page_size = 2

    def get_queryset(self):
        if self.request.user.is_staff: # type: ignore
            return models.Todo.objects.all()
        return models.Todo.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=False, methods=['post'])
    def filter(self, request):
        user = request.user
        if user.is_authenticated:
            if user.is_staff:
                queryset = models.Todo.objects.all()
            else:
                queryset = models.Todo.objects.filter(owner=user)
            
            # Apply filters from request data
            filter_values = request.data
            todo_filter = TodoFilter(filter_values, queryset=queryset)
            filtered_queryset = todo_filter.qs
            
            # Paginate the filtered queryset
            page = self.paginate_queryset(filtered_queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(filtered_queryset, many=True)
            return Response(serializer.data)
        
        return Response(status=status.HTTP_401_UNAUTHORIZED)

class UserCreate(views.APIView):
    permission_classes = [AllowAny]
    # User registration
    @extend_schema(
        request=UserSerializer,
        responses={201: UserSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogin(views.APIView):
    permission_classes = [AllowAny]
    authentication_classes = [SessionAuthentication]
    @extend_schema(
        request=inline_serializer(
            name='LoginSerializer',
            fields={
                'username': serializers.CharField(),
                'password': serializers.CharField(write_only=True)
            }
        ),
        responses={200: OpenApiTypes.OBJECT}
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.check_user(request.data)
            login(request, user)
            return Response(serializer.data, status=status.HTTP_200_OK)

class UserLogout(views.APIView):
    permission_classes = [AllowAny]
    @extend_schema(
        request=None, 
        responses={200: OpenApiTypes.OBJECT}
    )
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)

class UserView(views.APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def get(self, request):
        if request.user.is_staff:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
        else:
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
