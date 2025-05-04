from rest_framework import serializers

from requirements.models import Requirement, RequirementSource, Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class RequirementSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequirementSource
        fields = '__all__'


class RequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requirement
        fields = '__all__'

class RequirementChildrenSerializer(serializers.ModelSerializer):
    children = RequirementSerializer(many=True, read_only=True)
    class Meta:
        model = Requirement
        fields = ['children']

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField(use_url=False)