from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth import models as auth
from django.utils.translation import gettext_lazy as _

from checked_csv.admin import CsvExportModelMixin, CsvImportModelMixin
from commndata.admin import UserAdminMixin, BaseTableAdminMixin, TimeLinedTableAdminMixin
from commndata.models import CodeCategory, CodeMaster


admin.site.unregister(auth.User)
admin.site.unregister(auth.Group)

@admin.register(auth.Group)
class GroupModelAdmin(CsvExportModelMixin, CsvImportModelMixin, GroupAdmin):
    pass

@admin.register(auth.User)
class UserModelAdmin(UserAdminMixin, CsvExportModelMixin, CsvImportModelMixin, UserAdmin):
    list_display = ['username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined', 'is_superuser']
    # export_fields = ('username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined', 'is_superuser')

class CodeCategoryModelAdmin(BaseTableAdminMixin, CsvExportModelMixin, CsvImportModelMixin, ModelAdmin):
    # import_field_names = ['codecategory', 'name']
    pass

admin.site.register(CodeCategory, CodeCategoryModelAdmin)

@admin.register(CodeMaster)
class CodeMasterModelAdmin(TimeLinedTableAdminMixin, CsvExportModelMixin, CsvImportModelMixin, ModelAdmin):
    list_display = ['codecategory', 'code', 'name', 'start_date', 'end_date']
    list_filter = ['codecategory__name', 'start_date']
    search_fields = ('codecategory__name', 'name')
    date_hierarchy = 'start_date'

    def get_readonly_fields(self, request, obj=None):
        fields = super(CodeMasterModelAdmin, self).get_readonly_fields(request, obj)
        if obj:
            return (*fields, 'codecategory')
        else:
            return fields

