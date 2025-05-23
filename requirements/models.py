from django.db import models
from simple_history.models import HistoricalRecords


# Create your models here.
class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    history = HistoricalRecords()


class RequirementSource(models.Model):
    name = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    history = HistoricalRecords()

class RequirementType(models.IntegerChoices):
    Requirement = 1
    Recommendation = 2
    Permission = 3
    Heading = 4
    Information = 5


class Applicability(models.IntegerChoices):
    Todo = 0
    Applicable = 1
    No = 2
    Modified = 3

class Requirement(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    source_reference = models.ForeignKey(RequirementSource, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', null=True)
    req_identifier = models.CharField(max_length=100)
    ie_puid = models.CharField(max_length=50, null=True)
    name = models.CharField(max_length=100)
    type = models.IntegerField(choices=RequirementType, null=True)
    applicability = models.IntegerField(choices=Applicability.choices, default=Applicability.Todo)
    applicability_comment = models.TextField(null=True, blank=True)
    requirement = models.TextField(null=True)
    notes = models.TextField(null=True, blank=True)
    caused_by = models.ManyToManyField('Requirement', related_name='causes', null=True, blank=True)
    mentions = models.ManyToManyField('Requirement', related_name='mentioned_by', null=True, blank=True)
    history = HistoricalRecords()


class Message(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    requirement = models.ForeignKey('Requirement', on_delete=models.CASCADE)
    text = models.TextField()