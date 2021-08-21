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
        Takes a POST request with a university object {"name": university_name} within the body.
        If successful, returns 200 OK with university data {"name": university_name, "url": university_url}
        :param request: object - request object.
        :return: str[] - list of valid universities.
        """
        if request.data:
            queried_university: dict = request.data
            deserializer = ParseUniversitiesSerializer(data=queried_university, many=False)
            engine = WebscrapingUtils()

            if deserializer.is_valid():
                deserialized_university = deserializer.validated_data
                valid_universities_names = [university.name for university in ValidUniversities.objects.all()]

                # Queried university is cached in our backend microservice - but is cached/valid in our webscraping
                # microservice.
                if deserialized_university in valid_universities_names:
                    # Serializes the valid university and returns it as a response.
                    serializer = ValidUniversitySerializer(data=ValidUniversities.objects.get(
                        name=deserialized_university).values())

                    if serializer.is_valid():
                        engine.quit()
                        return Response(data=serializer.validated_data, status=status.HTTP_200_OK)

                    else:
                        engine.quit()
                        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                # Queried university is not cached in either microservice.
                else:
                    university_name = deserialized_university["name"]
                    # Check if the university is on the site, and thus is able to be scraped. 3 retries.
                    retries = 3
                    for i in range(retries):
                        university_name, university_url = engine.university_is_valid(
                            university_name=university_name)

                        if university_name is not None and university_url is not None:
                            # Navigate to university url.
                            engine.get(university_url)
                            offer_rate, acceptance_rate = engine.get_offer_and_acceptance_rate()
                            tef = engine.get_tef_rating()
                            ucas_points = engine.get_university_ucas_points()
                            engine.quit()

                            return Response(data={
                                "name": university_name,
                                "url": university_url,
                                "offer_rate": offer_rate,
                                "acceptance_rate": acceptance_rate,
                                "tef": tef,
                                "ucas_points": ucas_points
                            }, status=status.HTTP_200_OK)

                        else:
                            pass

                    engine.quit()

            # Deserialization failed
            else:
                engine.quit()
                return Response(data=deserializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListValidUniversities(ListAPIView):
    queryset = ValidUniversities.objects.all()
    serializer_class = ValidUniversitySerializer


class ScrapeUniversityAccommodations(APIView):
    """
    Scrapes all of the halls from the URL of a SINGLE university.
    """
    def post(self, request):
        """
        Request.data MUST contain the university with fields: ["name", "url"]
        :param request:
        :return:
        """
        if request.data:
            serializer = ValidUniversitySerializer(data=request.data, many=False)
            webscraping_utils = WebscrapingUtils()

            if serializer.is_valid():
                # List of accommodation data [{"name": str, "postcode": str...}, ...]
                university_accommodation_data = []
                university_name, university_url = serializer.validated_data["name"], serializer.validated_data["url"]
                # List of accommodation urls.
                accommodation_urls = webscraping_utils.get_university_accommodation_urls(university_url=university_url)

                for accommodation_url in accommodation_urls:
                    # Retrieves data from accommodation url.
                    university_accommodation_data.append(webscraping_utils.get_accommodation_data(accommodation_url=
                                                                                                  accommodation_url))

                return Response(data=university_accommodation_data, status=status.HTTP_200_OK)

            else:
                return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)