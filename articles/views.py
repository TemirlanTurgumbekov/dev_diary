from rest_framework import generics, permissions
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from .models import *
from .serializers import *
from .permissions import *


class ArticleListView(generics.ListAPIView):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.role == 'subscriber':
            subscriptions = Subscription.objects.filter(subscriber=user).values_list('author', flat=True)
            return Article.objects.filter(
                models.Q(status=Article.PUBLIC) |
                models.Q(status=Article.PRIVATE, author__in=subscriptions)
            )
        return Article.objects.filter(status=Article.PUBLIC)
    

class ArticleCreateView(generics.CreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthor]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ArticleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self):
        article = super().get_object()
        if article.status == Article.PRIVATE and self.request.user != article.author:
            if not self.request.user.is_authenticated or self.request.user.role != 'subscriber':
                raise PermissionDenied("You do not have permission to view this article.")
            if not Subscription.objects.filter(subscriber=self.request.user, author=article.author).exists():
                raise PermissionDenied("You do not have permission to view this article.")
        return article 


class SubscribeView(generics.CreateAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        author = serializer.validated_data['author'] 
        subscriber = self.request.user


        if Subscription.objects.filter(subscriber=subscriber, author=author).exists():
            return Response({'detail': 'You are already subscribed to this author.'}, status=status.HTTP_400_BAD_REQUEST)
        
        Subscription.objects.create(subscriber=subscriber, author=author)

        return Response({'detail': 'Subscription created successfully.'}, status=status.HTTP_201_CREATED)