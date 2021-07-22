from rest_framework.serializers import Serializer, ModelSerializer
from rest_framework.fields import CharField

from .models import ValidUniversities


class ParseUniversitiesSerializer(Serializer):
    name = CharField(max_length=100, required=True)


class ValidUniversitySerializer(ModelSerializer):
    class Meta:
        model = ValidUniversities
        fields = "__all__"
