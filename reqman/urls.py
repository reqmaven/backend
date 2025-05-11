"""
URL configuration for reqman project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import routers
from rest_framework.authtoken import views

from requirements.views import RequirementViewSet, RequirementImportView, ProjectsViewSet, RequirementSourceViewSet, \
    RequirementChildrenViewSet, ProjectRequirementImportView, ProjectRequirementSourceImportView

router = routers.DefaultRouter()
router.register(r'project', ProjectsViewSet)
router.register(r'requirement-source', RequirementSourceViewSet)
router.register(r'requirements', RequirementViewSet)
router.register(r'requirement-childrens', RequirementChildrenViewSet, basename='a')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', views.obtain_auth_token),
    path('requirements_import', RequirementImportView.as_view()),
    path('project_requirements_import', ProjectRequirementImportView.as_view()),
    path('project_requirements_sources_import', ProjectRequirementSourceImportView.as_view()),
]
