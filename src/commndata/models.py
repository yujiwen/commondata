from django.db import models
from django.utils.translation import gettext_lazy as _
from datetime import date
from django.utils import timezone


# Create your models here.
class BaseTable(models.Model):
    version = models.IntegerField(verbose_name = _('version'), blank = False, default = 1)
    created_at = models.DateTimeField(verbose_name = _('created_at'), blank = False, serialize=False)
    creator = models.CharField(max_length = 120, verbose_name = _('creator'), blank = False, serialize=False)
    updated_at = models.DateTimeField(verbose_name = _('updated_at'), blank = False, serialize=False)
    updater = models.CharField(max_length = 120, verbose_name = _('updater'), blank = False, serialize=False)
    delete_flag = models.BooleanField(blank=False, verbose_name = _('delete flag'), null=False, default=False)

    class Meta:
        abstract = True
    
    @staticmethod
    def get_init_values(username: str):
        return  {
            'creator': username,
            'created_at': timezone.now(),
            'updater': username,
            'updated_at': timezone.now(),
            'version': 1,
        }

    def set_update_values(self, updater: str):
        self.updater = updater
        self.updated_at = timezone.now()
        self.version += 1

    @staticmethod
    def get_noninputable_fields():
        return ('creator', 'created_at', 'updater', 'updated_at', 'version')

    @staticmethod
    def get_autoupdatable_fields():
        return ('updater', 'updated_at', 'version')

    @staticmethod
    def get_update_info_fieldsets():
        return [('creator', 'created_at'), ('updater', 'updated_at', 'version')]

    @staticmethod
    def get_validity_info_fieldsets():
        return [('delete_flag',)]

class TimeLinedTable(BaseTable):
    start_date = models.DateField(verbose_name = _('start_date'), blank = False, null = False)
    end_date = models.DateField(verbose_name = _('end_date'), blank = True, null = True)

    class Meta:
        abstract = True

    @staticmethod
    def get_validity_info_fieldsets():
        return [('start_date', 'end_date', 'delete_flag')]

class CodeCategory(BaseTable):
    codecategory = models.CharField(max_length=32, verbose_name=_('code category'))
    name = models.CharField(max_length=128, verbose_name=_('name'))
    display_order = models.IntegerField(blank=True, null=True)                      # 表示順

    class Meta:
        verbose_name = _('code category')
        verbose_name_plural = _('code category')
        constraints = [
            models.UniqueConstraint(name='codecategory_unique', fields = ['codecategory']), 
        ]
        ordering = ['display_order']
        permissions = [
            ('import_codecategory', 'Can import Code Category'),
            ('export_codecategory', 'Can export Code Category'),
        ]

    def __str__(self):
        return self.name

class CodeMaster(TimeLinedTable):
    codecategory = models.ForeignKey('CodeCategory', verbose_name=_('code category'), on_delete=models.RESTRICT)
    code = models.CharField(max_length=32, verbose_name=_('code'))                  # コード
    name = models.CharField(max_length=128, verbose_name=_('name'))                 # コード名
    value = models.CharField(max_length=128, verbose_name=_('value'), blank=True)   # コード値
    display_order = models.IntegerField(blank=True, null=True)                      # 表示順

    class Meta:
        verbose_name = _('code master')
        verbose_name_plural = _('code master')
        constraints = [
            models.UniqueConstraint(name='codemaster_unique', fields = ['start_date', 'codecategory', 'code']), 
        ]
        ordering = ['codecategory', 'display_order', 'code', '-start_date',]
        permissions = [
            ('import_codemaster', 'Can import Code Master'),
            ('export_codemaster', 'Can export Code Master'),
        ]
    
    def __str__(self):
        return self.name
