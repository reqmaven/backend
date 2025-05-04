import csv
from .models import Project, RequirementSource, Requirement

type_map = {'Requirement': 0,
            'Recommendation': 1}
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


def import_requirements(file):
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
                    'type': type_map[row['Type']],
                    'ie_puid': row['IE PUID'],
                    'requirement': row['Original requirement'],
                    'notes': row['Text of Note of Original requirement']
                }
            )