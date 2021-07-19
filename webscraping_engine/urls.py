from django.urls import path
from .views import ParseUniversities

urlpatterns = [
    path("parse-universities", ParseUniversities.as_view(), name='parse-universities')
]
