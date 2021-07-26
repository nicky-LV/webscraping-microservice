from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status

from .utils import WebscrapingUtils
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

        many = False
        # Conditionally set the "many" kwarg. True if len(university_list) > 1, else False
        if len(university_list) > 1:
            many = True

        deserializer = ParseUniversitiesSerializer(data=university_list, many=many)
        webscraping_utils = WebscrapingUtils()

        if deserializer.is_valid():
            universities = deserializer.validated_data
            valid_universities = [{"name": university.name, "url": university.url} for university in
                                  ValidUniversities.objects.all()]

            for idx, university in enumerate(universities):
                if university in valid_universities:
                    pass

                else:
                    university = university["name"]
                    # Check if the university is on the site, and thus is able to be scraped. 5 retries.
                    retries = 3
                    for i in range(retries):
                        university_name, university_url = webscraping_utils.university_is_valid(university_name=university)

                        if university_name and university_url:
                            valid_universities.append({
                                "name": university_name,
                                "url": university_url
                            })
                            # Break loop if it's successful.
                            break

                        else:
                            pass

            return Response(data=valid_universities, status=status.HTTP_200_OK)

        else:
            print(deserializer.errors)
            return Response(data=deserializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListValidUniversities(ListAPIView):
    queryset = ValidUniversities.objects.all()
    serializer_class = ValidUniversitySerializer


class ScrapeUniversityAccommodations(APIView):
    """
    Scrapes all of the halls from the URL of a SINGLE university.
    """
    def post(self, request):
        serializer = ValidUniversitySerializer(request.data, many=False)
        webscraping_utils = WebscrapingUtils()

        if serializer.is_valid():
            # List of accommodation data [{"name": str, "postcode": str...}, ...]
            university_accommodation_data = []
            university_name, university_url = serializer.validated_data["name"], serializer.validated_data["url"]
            # List of accommodation urls.
            accommodation_urls = webscraping_utils.get_university_accommodation_urls(university_url=university_url)

            for accommodation_url in accommodation_urls:
                # Retrieves data from accommodation url.
                university_accommodation_data.append(webscraping_utils.get_accommodation_data(accommodation_url=accommodation_url))

            return Response(data=university_accommodation_data, status=status.HTTP_200_OK)

        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
