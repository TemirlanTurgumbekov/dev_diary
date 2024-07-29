from django.urls import path
from .views import *

urlpatterns = [
    path('/', ArticleListView.as_view(), name='article-list'),
    path('/create/', ArticleCreateView.as_view(), name='article-create'),
    path('/<int:pk>/', ArticleView.as_view(), name='article-detail'),
    path('/subscribe/', SubscribeView.as_view(), name='subscribe'),
]
