from rest_framework import generics, mixins, status, permissions
from rest_framework.response import Response
from .models import SiteSettings
from .serializers import SiteSettingsSerializer


class SiteSettingsListCreateAPIView(
    mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView
):
    queryset = SiteSettings.objects.all()
    serializer_class = SiteSettingsSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class SiteSettingsDetailAPIView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    queryset = SiteSettings.objects.all()
    serializer_class = SiteSettingsSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
