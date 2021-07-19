from rest_framework.serializers import Serializer
from rest_framework.fields import CharField


class ParseUniversitiesSerializer(Serializer):
    name = CharField(max_length=50, required=True)
