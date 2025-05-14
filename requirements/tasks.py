import csv
import shutil
from pathlib import Path
from .models import Project, RequirementSource, Requirement, RequirementType
from .requirementsData import RequirementData


type_map = {'Requirement': 1,
            'Recommendation': 2,
            'Permission': 3,
            'Heading': 4,
            'Information': 5}

applicability_map = {'': 0,
                     'Y': 1,
                     'y': 1,
                     'N': 2,
                     'n': 2,
                     'P': 3}

def import_project_compressed(filepath: Path, project, user):
    work_dir = filepath.parent.joinpath('workdir')
    work_dir.mkdir(parents=True, exist_ok=True)
    shutil.unpack_archive(filepath.resolve(), extract_dir=work_dir)
    for req_file in work_dir.glob('*.csv'):
        print("Importing", req_file)
        source, created = RequirementSource.objects.get_or_create(
            name=req_file.stem,
            project=project,
            defaults={
                'created_by': user
            }
        )
        with open(req_file, 'r', encoding='utf-8') as f:
            import_project_requirements(f, source, user)

def import_project_requirements(file, source_reference, user):
    #f = file.read().decode('utf-8')
    #reader = csv.DictReader(io.StringIO(f))
    reader = csv.DictReader(file)
    fields = set(reader.fieldnames)
    if fields >= {'ID', 'Object Heading and Object Text', 'Rationale/Comment', 'Object Type', 'Applicability',
                  'Applicability Comment'}:
        import_project_requirements_v2(source_reference, reader, user)
    elif fields >= {'ID', 'Rationale/Comment', 'Req. Identifier', 'Section', 'Title', 'Text', 'Applicability', 'Applicability Comment'}:
        import_project_requirements_v1(source_reference, reader, user)


def get_parent(project, source_reference, section, user):
    identifier = section
    number = "".join(filter(str.isnumeric, identifier))
    if '.' in identifier:
        identifier_last_level = identifier[identifier.rfind('.')+1:]
        identifier = identifier[:identifier.rfind('.')]
        req_id = None
        parent = None
        for req in identifier.split('.'):
            if req_id is None:
                req_id = req
            else:
                req_id = req_id + '.' + req
            parent, created = Requirement.objects.get_or_create(project=project,
                                                                source_reference=source_reference,
                                                                name=req_id,
                                                                type=RequirementType.Heading,
                                                                defaults={'parent': parent,
                                                                          'created_by': user})
        if len(identifier_last_level) > 0:
            suffix = identifier_last_level.strip('0123456789')
            prefix = identifier_last_level[:len(suffix)]
            if len(prefix) > 0:
                req_id = req_id + '.' + prefix
                parent, created = Requirement.objects.get_or_create(project=project, source_reference=source_reference,
                                                                    name=req_id, req_identifier=req_id,
                                                                    defaults={'parent': parent,
                                                                          'created_by': user})
        return parent
    elif identifier != number:
        parent, created= Requirement.objects.get_or_create(
            project=project,
            source_reference=source_reference,
            name=number,
            req_identifier=number,
            defaults={
                'created_by': user
            }
        )
        return parent
    else:
        return None


def import_requirements(file, user):
    with open(file.temporary_file_path()) as f:
        reader = csv.DictReader(f)
        for row in reader:
            print(row)
            project, created = Project.objects.get_or_create(
                name=row['DOORS Project'],
                defaults={
                    'created_by': user
                }
            )
            source_reference, created = RequirementSource.objects.get_or_create(
                name=row['ECSS Source Reference'],
                project=project,
                defaults={
                    'created_by': user
                }
            )
            req, created = Requirement.objects.update_or_create(
                project=project,
                source_reference=source_reference,
                parent=get_parent(project, source_reference, row['ECSS Req. Identifier'], user),
                name=row['ECSS Req. Identifier'],
                req_identifier=row['ECSS Req. Identifier'],
                defaults={
                    'type': type_map[row['Type']],
                    'ie_puid': row['IE PUID'],
                    'requirement': row['Original requirement'],
                    'notes': row['Text of Note of Original requirement'],
                    'created_by': user,
                }
            )


def import_project_requirements_v1(source_reference, reader, user):
    for row in reader:
        print(row)

        data = RequirementData()
        data.id = row['ID'].strip()
        data.section = row['Title'].strip()
        data.requirement_type = RequirementType.Requirement
        data.requirement_text = row['Text'].strip()
        data.notes = row['Rationale/Comment'].strip()
        data.ie_puid = row['Req. Identifier'].strip()
        data.applicability = applicability_map[row['Applicability']]
        data.applicability_comment = row['Applicability Comment'].strip()

        parent_req = get_parent(source_reference.project, source_reference, data.section, user)
        requirement_update_or_create(source_reference, parent_req, user, data)


def import_project_requirements_v2(source_reference, reader, user):
    parent_req = None
    data = RequirementData()
    for row in reader:
        print(row)

        data.id = row['ID'].strip()
        data.requirement_type = type_map[row['Object Type']]
        if 'Applicability' in row:
            data.applicability = applicability_map[row['Applicability']]
            data.applicability_comment = row['Applicability Comment'].strip()

        if data.requirement_type == RequirementType.Heading:
            object_text_split = row['Object Heading and Object Text'].split(' ', 1)
            data.section = object_text_split[0].strip().rstrip('.')
            data.requirement_text = object_text_split[1].strip()
        elif data.requirement_type == RequirementType.Information:
            data.requirement_text = row['Object Heading and Object Text'].strip()
        elif data.requirement_type == RequirementType.Requirement:
            a = row['Object Heading and Object Text'].find(' ')
            b = row['Object Heading and Object Text'].find('\n')
            if a == -1:
                split = b
            elif b == -1:
                split = a
            else:
                split = min(a, b)
            object_text_split = row['Object Heading and Object Text'][:split]
            reqid_history_verification = object_text_split.split('/')
            data.ie_puid = reqid_history_verification[0].strip()
            #data.allowed_verification_methods = allowed_verification
            data.requirement_text = row['Object Heading and Object Text'][split+1:].strip()

        if data.requirement_type == RequirementType.Heading:
            parent_req = get_parent(source_reference.project, source_reference, data.section, user)

        req = requirement_update_or_create(source_reference, parent_req, user, data)
        if data.requirement_type == RequirementType.Heading:
            parent_req = req


def requirement_update_or_create(source_reference, parent_req, user, data: RequirementData):
    req, created = Requirement.objects.update_or_create(
        project=source_reference.project,
        source_reference=source_reference,
        parent=parent_req,
        name=data.section,
        defaults={
            'req_identifier': data.id,
            'type': data.requirement_type,
            'ie_puid': data.ie_puid,
            'requirement': data.requirement_text,
            'notes': None,
            'applicability': data.applicability,
            'applicability_comment': data.applicability_comment,
            'created_by': user,
        }
    )
    return req