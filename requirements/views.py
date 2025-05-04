import csv

from rest_framework import viewsets, views, filters
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Requirement, Project, RequirementSource
from .serializers import RequirementSerializer, FileUploadSerializer, ProjectSerializer, RequirementSourceSerializer, \
    RequirementChildrenSerializer
from django_filters.rest_framework import DjangoFilterBackend


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


def get_parent(project, source_reference, row):
    identifier = row['ECSS Req. Identifier']
    number = "".join(filter(str.isnumeric, identifier))
    if '.' in identifier:
        identifier = identifier[:identifier.rfind('.')]
        req_id = None
        parent = None
        for req in identifier.split('.'):
            if req_id is None:
                req_id = req
            else:
                req_id = req_id + '.' + req
            print(req, req_id)
            parent, created = Requirement.objects.get_or_create(project=project, source_reference=source_reference, name=req_id, req_identifier=req_id, defaults={'parent': parent})
        return parent
    elif identifier != number:
        parent, created= Requirement.objects.get_or_create(project=project, source_reference=source_reference, name=number, req_identifier=number)
        return parent
    else:
        return None


class RequirementImportView(views.APIView):
    serializer_class = FileUploadSerializer

    def post(self, request):
        file = request.FILES['file']
        print(file)
        with open(file.temporary_file_path()) as f:
            reader = csv.DictReader(f)
            for row in reader:
                print(row)
                project, created = Project.objects.get_or_create(name=row['DOORS Project'])
                source_reference, created = RequirementSource.objects.get_or_create(name=row['ECSS Source Reference'],
                                                                                    project=project)
                req, created = Requirement.objects.update_or_create(
                    project=project,
                    source_reference=source_reference,
                    parent=get_parent(project, source_reference, row),
                    name=row['ECSS Req. Identifier'],
                    req_identifier=row['ECSS Req. Identifier'],
                    defaults={
                            'type': row['Type'],
                            'ie_puid': row['IE PUID'],
                            'requirement': row['Original requirement'],
                            'notes': row['Text of Note of Original requirement']
                    }
                )
        return Response()