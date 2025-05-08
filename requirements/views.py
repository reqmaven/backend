import tempfile

from pathlib import Path
from rest_framework import viewsets, views, filters
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.core.files.storage import FileSystemStorage
from .models import Requirement, Project, RequirementSource
from .serializers import RequirementSerializer, FileUploadSerializer, ProjectSerializer, RequirementSourceSerializer, \
    RequirementChildrenSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .tasks import import_requirements, import_project_requirements, import_project_compressed


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000
# Create your views here.
class ProjectsViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class RequirementSourceViewSet(viewsets.ModelViewSet):
    queryset = RequirementSource.objects.all()
    serializer_class = RequirementSourceSerializer
    filterset_fields = {'project': ['exact']}
    pagination_class = StandardResultsSetPagination

class RequirementViewSet(viewsets.ModelViewSet):
    queryset = Requirement.objects.all()
    serializer_class = RequirementSerializer
    filterset_fields = {'project': ['exact', 'in'],
                        'source_reference': ['exact', 'in'],
                        'type': ['exact', 'in'],
                        'applicability': ['exact', 'in'],
                        'parent': ['exact', 'isnull']}
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['requirement', 'notes']


class RequirementChildrenViewSet(viewsets.ModelViewSet):
    queryset = Requirement.objects.all()
    serializer_class = RequirementChildrenSerializer


class RequirementImportView(views.APIView):
    serializer_class = FileUploadSerializer

    def post(self, request):
        file = request.FILES['file']
        print(file)
        try:
            import_requirements(file)
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
            import_project_requirements(file, requirement_source)
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
            import_project_compressed(filepath, project)
        except Exception as e:
            print("Exception", e)

        return Response()