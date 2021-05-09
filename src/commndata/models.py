from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.functional import cached_property
from django.core.exceptions import ObjectDoesNotExist

# Create your models here.
class BaseTable(models.Model):
    version = models.IntegerField(verbose_name = _('version'), blank = False, default = 1)
    created_at = models.DateTimeField(verbose_name = _('created_at'), blank = False, serialize=False)
    creator = models.CharField(max_length = 120, verbose_name = _('creator'), blank = False, serialize=False)
    updated_at = models.DateTimeField(verbose_name = _('updated_at'), blank = False, serialize=False)
    updater = models.CharField(max_length = 120, verbose_name = _('updater'), blank = False, serialize=False)

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
    def get_readonly_fields():
        """
        Read only fields by means of Django Admin Site definition.
        By means of HTML, they are only div tags, which are classed as readonly.
        """
        return ('creator', 'created_at', 'updater', 'updated_at')

    @staticmethod
    def get_html_readonly_fields():
        """
        By means of HTML, they are input tags with readonly attribute.
        """
        return {'version'}

    @staticmethod
    def get_autoupdatable_fields():
        return ('updater', 'updated_at', 'version')

    @staticmethod
    def get_update_info_fieldsets():
        return [('creator', 'created_at'), ('updater', 'updated_at', 'version')]

    @staticmethod
    def get_validity_info_fieldsets():
        return ()

    def optimistic_violation_check(self) -> None:
        """
        Optimistic violation check using version field.
        """
        if self.pk:
            latest = self.__class__.objects.get(pk=self.pk)
            if latest.version > self.version:
                # name = self._meta.verbose_name.title()
                raise ValidationError(_('This %(name)s maybe already changed by other users. Please reopen the screen.'%{'name': self}))

    def clean(self) -> None:
        super(BaseTable, self).clean()

        self.optimistic_violation_check()

class TimeLinedTable(BaseTable):
    start_date = models.DateField(verbose_name = _('start_date'), blank = False, null = False)
    end_date = models.DateField(verbose_name = _('end_date'), blank = True, null = True)

    class Meta:
        abstract = True

    @staticmethod
    def get_validity_info_fieldsets():
        return [('start_date', 'end_date')]

    @cached_property
    def get_model_unique_key(self) -> tuple:
        """
        Get a unique constraint named after the model, if there is one.
        All fields contained in this unique constraint is supposed to be not nullable.
        For example: model CodeMaster's supposed unique constraint name is 'codemaster_unique'.
        """
        if not self._meta.constraints:
            return ()

        unique_constraint_name = '%s_unique' % self._meta.model_name
        unique_constraint = next(filter(lambda c: c.name == unique_constraint_name, self._meta.constraints), None)
        if not unique_constraint:
            return ()

        return unique_constraint.fields
    
    @cached_property
    def get_model_unique_values(self) -> dict:
        return {k:getattr(self, k) for k in self.get_model_unique_key}

    @cached_property
    def get_model_constraint_values(self) -> dict:
        return {k:getattr(self, k) for k in self.get_model_unique_key if k != 'start_date'}

    def newer_record(self):
        """
            Detect if there is a record with a newer start_date.
            Here the unique constraint must contains a start_date field.
        """
        newer_records = self.__class__.objects.filter(**self.get_model_constraint_values) \
                        .filter(start_date__gt=self.start_date) \
                        .order_by('start_date')
        if newer_records:
            return newer_records[0]
        else:
            None
    
    def older_record(self):
        """
            Detect if there is a record with a older start_date.
            Here the unique constraint must contains a start_date field.
        """
        older_records = self.__class__.objects.filter(**self.get_model_constraint_values) \
                        .filter(start_date__lt=self.start_date) \
                        .order_by('-start_date')
        if older_records:
            return older_records[0]
        else:
            None

    def history_check(self):
        """
        If there is a newer record(start_date is newer), then create and update are not allowed.
        """
        try:
            newer_record = self.newer_record()
            if newer_record and self != newer_record:
                # name = self._meta.verbose_name.title()
                raise ValidationError(_('We have a newer %s, so we can not save this record.' % self))
        except ObjectDoesNotExist:
            # This error should be already captured by other validations, so we ignore it here.
            pass

    def clean(self) -> None:
        super(TimeLinedTable, self).clean()
        self.history_check()

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
