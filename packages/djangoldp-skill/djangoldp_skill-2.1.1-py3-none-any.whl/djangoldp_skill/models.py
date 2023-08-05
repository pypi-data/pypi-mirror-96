from django.conf import settings
from django.db import models
from djangoldp_i18n.views import I18nLDPViewSet

from djangoldp.models import Model

class Skill(Model):
    name = models.CharField(max_length=255, default='', null=True, blank=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="skills")

    class Meta:
        serializer_fields=["@id", "name"]
        nested_fields=[]
        anonymous_perms = ['view']
        container_path = 'skills/'
        rdf_type = 'hd:skill'
        view_set = I18nLDPViewSet


    def __str__(self):
        return self.name
