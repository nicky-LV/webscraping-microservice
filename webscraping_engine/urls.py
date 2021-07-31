from django.urls import path
from .views import *

urlpatterns = [
    path("parse-universities/", ParseUniversities.as_view(), name='parse-universities'),
    path("valid-universities/", ListValidUniversities.as_view(), name='list-valid-universities'),
    path("scrape-accommodations/", ScrapeUniversityAccommodations.as_view(), name='scrape-university-accommodations')
]
