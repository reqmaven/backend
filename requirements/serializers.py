from rest_framework import serializers

from requirements.models import Requirement, RequirementSource, Project, Message


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
        fields = ['id', 'name', 'project', 'description', 'created_at', 'history']


class RequirementSerializer(serializers.ModelSerializer):
    has_children = serializers.SerializerMethodField()
    history = HistoricalRecordField(read_only=True)

    class Meta:
        model = Requirement
        fields = ['id', 'project', 'source_reference', 'parent', 'req_identifier', 'ie_puid', 'name', 'type',
                  'applicability', 'applicability_comment', 'requirement', 'notes', 'history', 'has_children']

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


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'requirement', 'created_by', 'text']


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'requirement', 'text']


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField(use_url=False)