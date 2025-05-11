from rest_framework import serializers

from requirements.models import Requirement, RequirementSource, Project

class HistoricalRecordField(serializers.ListField):
    child = serializers.DictField()

    def to_representation(self, data):
        return super().to_representation(data.values())

class ProjectSerializer(serializers.ModelSerializer):
    history = HistoricalRecordField(read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'created_at', 'history']


class RequirementSourceSerializer(serializers.ModelSerializer):
    history = HistoricalRecordField(read_only=True)

    class Meta:
        model = RequirementSource
        fields = '__all__'


class RequirementSerializer(serializers.ModelSerializer):
    has_children = serializers.SerializerMethodField()
    history = HistoricalRecordField(read_only=True)

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