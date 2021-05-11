from itertools import filterfalse
from django.contrib import admin
from django.contrib.admin.utils import flatten
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import datetime

from commndata.forms import SuperUserAuthenticationForm, ActiveUserAuthenticationForm
from commndata.models import BaseTable


def disable_field(widget):
    if widget.input_type == 'checkbox':
        widget.attrs['disabled'] = 'true'
    else:
        widget.attrs['readonly'] = 'true'
        widget.attrs['style'] = 'border: none transparent; outline: none'
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

            if obj and obj == request.user:
                disabled_fields |= {'is_staff', 'is_active', 'user_permissions',}

            if obj and obj != request.user:
                disabled_fields |= { 'first_name', 'last_name', 'email', }

        for field in filter(lambda f: f in form.base_fields, disabled_fields):
            form.base_fields[field].disabled = True

        return form

class BaseTableAdminMixin():
    """
    This is intended to be mixed with django.contrib.admin.ModelAdmin, and used to register BaseTable class
    """
    save_on_top = False

    def get_readonly_fields(self, request, obj=None) -> tuple[str]:
        """
        override of the ModelAdmin
        """
        return (*super(BaseTableAdminMixin, self).get_readonly_fields(request, obj), *self.model.get_readonly_fields())

    def get_csv_excluded_fields(self) -> list[str]:
        """
        override CsvImportModelMixin
        """
        return super(BaseTableAdminMixin, self).get_csv_excluded_fields() + list(self.model.get_readonly_fields())

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
    
    def get_validity_fieldsets(self, request, obj=None):
        if self.model.get_validity_info_fieldsets():
            return [(_('validity'), {'fields': self.model.get_validity_info_fieldsets()})] if obj else []
        else:
            return []

    def get_update_info_fieldsets(self, request, obj=None):
        if self.model.get_update_info_fieldsets():
            return [(_('Update Information'), {'fields': self.model.get_update_info_fieldsets()})] if obj else []
        else:
            return []

    def get_fieldsets(self, request, obj=None):
        """
        override of the ModelAdmin
        ・削除フラグを有効期間欄にて表示する
        ・作成者、作成日時、更新者、更新日時をまとめて更新情報欄にて表示する
        """

        def get_none_fieldsets():
            collected_fields = flatten(self.model.get_validity_info_fieldsets()) + flatten(self.model.get_update_info_fieldsets())
            return list(filterfalse(lambda f: f in collected_fields, self.get_fields(request, obj)))

        return (self.fieldsets or [(None, {'fields': get_none_fieldsets()})]) \
                + self.get_validity_fieldsets(request, obj) \
                + self.get_update_info_fieldsets(request, obj)

    def get_html_readonly_fields(self, request, obj=None, **kwargs):
        return self.model.get_html_readonly_fields()

    def get_form(self, request, obj=None, **kwargs):
        """
        override of the ModelAdmin
        """
        form = super(BaseTableAdminMixin, self).get_form(request, obj, **kwargs)

        readonly_field_widgets = [form.base_fields[f].widget for f in form.base_fields if f in self.get_html_readonly_fields(request, obj, **kwargs)]
        for widget in readonly_field_widgets:
            disable_field(widget)

        return form

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
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save_and_continue'] = False
        extra_context['show_close'] = True
        return super(TimeLinedTableAdminMixin, self).changeform_view(request, object_id, form_url, extra_context)
    
    def has_delete_permission(self, request, obj=None):
        """
        """
        if obj and obj.newer_record():
            return False
        else:
            return super(TimeLinedTableAdminMixin, self).has_delete_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if obj and obj.newer_record():
            return False
        else:
            return super(TimeLinedTableAdminMixin, self).has_change_permission(request, obj)


    def get_validity_fieldsets(self, request, obj=None):
        return [(_('validity'), {'fields': self.model.get_validity_info_fieldsets()})]

    # def get_form(self, request, obj=None, **kwargs):
    #     """
    #     Just the newest record is editable, the older records are disable to editing.
    #     """
    #     form = super(TimeLinedTableAdminMixin, self).get_form(request, obj, **kwargs)
    #     if obj and obj.newer_record():
    #         for widget in [form.base_fields[f].widget for f in form.base_fields]:
    #             disable_field(widget)

    #     return form

    def save_model(self, request, obj, form, change):
        if change:
            older_record = obj.older_record()
            if older_record and obj != older_record:
                older_record.end_date = obj.start_date - datetime.timedelta(days=1)
                older_record.set_update_values(request.user.username)
                older_record.save()
        
        super(TimeLinedTableAdminMixin, self).save_model(request, obj, form, change)
