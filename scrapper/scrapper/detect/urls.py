from django.urls import path
from .views import *
from .insta import instagram
from .fb import facebook

urlpatterns = [
    path('', homepage, name='homepage'),  # Home page URL
    path('instagram/', instagram, name='instagram'),  
    path('facebook/', facebook, name='facebook'),  
    path('twitter/', twitter, name='twitter'),  
]
