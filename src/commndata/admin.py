from itertools import filterfalse
from django.contrib import admin
from django.contrib.admin.utils import flatten
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from commndata.forms import SuperUserAuthenticationForm, ActiveUserAuthenticationForm
from commndata.models import BaseTable

class SuperUserOnlyAdminSite(admin.AdminSite):
    enable_nav_sidebar = True
    _empty_value_display = '-'

    login_form = SuperUserAuthenticationForm

    def has_permission(self, request):
        """
        Give permission to superuser only.
        """
        return request.user.is_superuser

class ActiveUserAdminSite(admin.AdminSite):
    enable_nav_sidebar = True
    _empty_value_display = '-'
    
    login_form = ActiveUserAuthenticationForm
    
    def has_permission(self, request):
        """
        Give permission to any active user.
        """
        return request.user.is_active

class UserAdminMixin():
    """
    This is intended to be mixed with django.contrib.admin.UserAdmin
    Restrict user account availability.
    """
    readonly_fields = ('date_joined', 'last_login',)

    def get_form(self, request, obj=None, **kwargs):
        """
        override of the ModelAdmin
        """
        form = super(UserAdminMixin, self).get_form(request, obj, **kwargs)
        disabled_fields = set()

        is_superuser = request.user.is_superuser
        if not is_superuser:
            # disabled for 'groups' is not working, maybe because it's a ManyToManyField?
            disabled_fields |= {'is_superuser', 'username', 'groups',}

            if obj is not None and obj == request.user:
                disabled_fields |= {'is_staff', 'is_active', 'user_permissions',}

            if obj is not None and obj != request.user:
                disabled_fields |= { 'first_name', 'last_name', 'email', }

        for field in filter(lambda f: f in form.base_fields, disabled_fields):
            form.base_fields[field].disabled = True

        return form

class BaseTableAdminMixin():
    """
    This is intended to be mixed with django.contrib.admin.ModelAdmin, and used to register BaseTable class
    """
    def get_readonly_fields(self, request, obj=None) -> tuple[str]:
        """
        override of the ModelAdmin
        """
        return (*super(BaseTableAdminMixin, self).get_readonly_fields(request, obj), *self.model.get_noninputable_fields())

    def get_csv_excluded_fields(self) -> list[str]:
        """
        override CsvImportModelMixin
        """
        return super(BaseTableAdminMixin, self).get_csv_excluded_fields() + list(self.model.get_noninputable_fields())

    def get_csv_excluded_fields_init_values(self, request) -> dict:
        """
        override CsvImportModelMixin
        """
        return super(BaseTableAdminMixin, self).get_csv_excluded_fields_init_values(request) | self.model.get_init_values(request.user.username)

    def update_csv_excluded_fields(self, request, row: BaseTable):
        """
        override CsvImportModelMixin
        """
        super(BaseTableAdminMixin, self).update_csv_excluded_fields(request, row)
        row.set_update_values(request.user.username)

    def get_update_fields(self) -> list[str]:
        """
        override CsvImportModelMixin
        """
        return super(BaseTableAdminMixin, self).get_update_fields() + list(self.model.get_autoupdatable_fields())
    
    def get_fieldsets(self, request, obj=None):
        """
        override of the ModelAdmin
        ・削除フラグを有効期間欄にて表示する
        ・作成者、作成日時、更新者、更新日時をまとめて更新情報欄にて表示する
        """

        def get_validity_fieldsets():
            return [(_('validity'), {'fields': self.model.get_validity_info_fieldsets()})] if obj else []

        def get_update_info_fieldsets():
            return [(_('Update Information'), {'fields': self.model.get_update_info_fieldsets()})] if obj else []
        
        def get_none_fieldsets():
            collected_fields = flatten(self.model.get_validity_info_fieldsets()) + flatten(self.model.get_update_info_fieldsets())
            return list(filterfalse(lambda f: f in collected_fields, self.get_fields(request, obj)))

        return (self.fieldsets or [(None, {'fields': get_none_fieldsets()})]) + get_validity_fieldsets() + get_update_info_fieldsets()

    def save_model(self, request, obj, form, change):
        obj.updater = request.user.username
        obj.updated_at = timezone.now()

        if change:
            obj.version = obj.version + 1
        else:
            obj.version = 1
            obj.creator = request.user.username
            obj.created_at = timezone.now()
        
        super(BaseTableAdminMixin, self).save_model(request, obj, form, change)


class TimeLinedTableAdminMixin(BaseTableAdminMixin):
    """
    This is intended to be mixed with django.contrib.admin.ModelAdmin
    """
