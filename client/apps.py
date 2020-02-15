from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ClientConfig(AppConfig):
    name = 'client'
    verbose_name = _('Client')
