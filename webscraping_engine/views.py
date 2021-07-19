from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from typing import List

from .serializers import ParseUniversitiesSerializer


class ParseUniversities(APIView):
    def post(self, request):
        """
        Takes a POST request with a list of universities within the body. Returns a list of valid universities that are
        can be scraped.
        :param request: object - request object.
        :return: str[] - list of valid universities.
        """
        university_list: List[str] = request.data
        serializer = ParseUniversitiesSerializer(university_list, many=True)

        if serializer.is_valid():
            universities = serializer.validated_data
            print(universities)
