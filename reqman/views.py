from django.contrib.auth.models import User
from rest_framework import viewsets, views, filters
from rest_framework.response import Response

from .serializers import UserSerializer


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class WhoAmIView(views.APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)
