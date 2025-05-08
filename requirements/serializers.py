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
    has_children = serializers.SerializerMethodField()
    class Meta:
        model = Requirement
        fields = '__all__'

    def get_has_children(self, obj):
        return obj.children.count() > 0


class RequirementMinimalSerializer(serializers.ModelSerializer):
    has_children = serializers.SerializerMethodField()
    class Meta:
        model = Requirement
        fields = ['id', 'name', 'type', 'applicability', 'requirement', 'ie_puid', 'has_children']

    def get_has_children(self, obj):
        return obj.children.count() > 0


class RequirementChildrenSerializer(serializers.ModelSerializer):
    children = RequirementMinimalSerializer(many=True, read_only=True)
    class Meta:
        model = Requirement
        fields = ['children']

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField(use_url=False)