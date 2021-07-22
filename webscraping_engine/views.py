from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status

from typing import List

from .utils import university_is_valid
from .serializers import ParseUniversitiesSerializer, ValidUniversitySerializer
from .models import ValidUniversities


class ParseUniversities(APIView):
    def post(self, request):
        """
        Takes a POST request with a list of universities within the body. Returns a list of valid universities that are
        can be scraped.
        :param request: object - request object.
        :return: str[] - list of valid universities.
        """
        university_list = request.data
        serializer = ParseUniversitiesSerializer(data=university_list, many=True)

        if serializer.is_valid():
            universities = serializer.validated_data
            valid_universities = [university.name for university in ValidUniversities.objects.all()]

            for idx, university in enumerate(universities):
                if university in valid_universities:
                    pass

                else:
                    university = university["name"]
                    # Check if the university is on the site, and thus is able to be scraped. 5 retries.
                    retries = 3
                    for i in range(retries):
                        university_name, university_url = university_is_valid(university_name=university,
                                                                              confirm_cookies=idx == 0)

                        if university_name and university_url:
                            valid_universities.append({
                                "name": university_name,
                                "url": university_url
                            })

                        else:
                            # Reduce retry number if university_is_valid returns False.
                            retries -= 1

            return Response(data=valid_universities, status=status.HTTP_200_OK)

        else:
            print(serializer.errors)
            return Response(data="Invalid universities provided", status=status.HTTP_400_BAD_REQUEST)


class ListValidUniversities(ListAPIView):
    queryset = ValidUniversities.objects.all()
    serializer_class = ValidUniversitySerializer
