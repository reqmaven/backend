import tempfile

from pathlib import Path
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, views, filters
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.core.files.storage import FileSystemStorage
from .models import Requirement, Project, RequirementSource, Message
from .serializers import RequirementSerializer, FileUploadSerializer, ProjectSerializer, RequirementSourceSerializer, \
    RequirementChildrenSerializer, MessageSerializer, MessageCreateSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .tasks import import_requirements, import_project_requirements, import_project_compressed


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000
# Create your views here.
class ProjectsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class RequirementSourceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = RequirementSource.objects.all()
    serializer_class = RequirementSourceSerializer
    filterset_fields = {'project': ['exact']}
    pagination_class = StandardResultsSetPagination

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class RequirementViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = Requirement.objects.all()
    serializer_class = RequirementSerializer
    filterset_fields = {'project': ['exact', 'in'],
                        'source_reference': ['exact', 'in'],
                        'type': ['exact', 'in'],
                        'applicability': ['exact', 'in'],
                        'parent': ['exact', 'isnull']}
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['requirement', 'notes']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class RequirementChildrenViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = Requirement.objects.all()
    serializer_class = RequirementChildrenSerializer


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = {'requirement': ['exact', 'in']}
    search_fields = ['text']

    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        else:
            return MessageSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class RequirementImportView(views.APIView):
    serializer_class = FileUploadSerializer

    def post(self, request):
        file = request.FILES['file']
        print(file)
        tmpdirname = Path(tempfile.mkdtemp())
        FileSystemStorage(location=tmpdirname).save(file.name, file)
        filepath = tmpdirname.joinpath(file.name)
        try:
            result = import_requirements.delay(str(filepath.resolve()), request.user.id)
            return Response({'task_id': result.task_id})
        except Exception as e:
            print(e)

        return Response()

class ProjectRequirementImportView(views.APIView):
    serializer_class = FileUploadSerializer

    def post(self, request):
        file = request.FILES['file']
        print(file, request.data)
        requirement_source_id = int(request.data['source_reference'])
        requirement_source = RequirementSource.objects.get(pk=requirement_source_id)
        print(requirement_source, requirement_source.project, requirement_source_id)
        try:
            import_project_requirements(file, requirement_source, request.user)
        except Exception as e:
            print("Exception", e)

        return Response()


class ProjectRequirementSourceImportView(views.APIView):
    serializer_class = FileUploadSerializer

    def post(self, request):
        file = request.FILES['file']
        print(file, request.data)
        project_id = int(request.data['project_id'])
        try:
            project = Project.objects.get(pk=project_id)
            tmpdirname = Path(tempfile.mkdtemp())
            FileSystemStorage(location=tmpdirname).save(file.name, file)
            filepath = tmpdirname.joinpath(file.name)
            result = import_project_compressed.delay(str(filepath.resolve()), project.id, request.user.id)
            return Response({'task_id': result.task_id})
        except Exception as e:
            print("Exception", e)

        return Response()