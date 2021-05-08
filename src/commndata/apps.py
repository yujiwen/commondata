from django.apps.config import AppConfig
from django.utils.translation import gettext_lazy as _


class CommonDataAppConfig(AppConfig):
    name = 'commndata'
    verbose_name = _('Common Data')