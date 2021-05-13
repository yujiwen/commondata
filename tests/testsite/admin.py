from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth import models as auth
from django.utils.translation import gettext_lazy as _

from checked_csv.admin import CsvExportModelMixin, CsvImportModelMixin
from commndata.admin import UserAdminMixin, BaseTableAdminMixin, TimeLinedTableAdminMixin
from commndata.models import CodeCategory, CodeMaster
from .forms import CodeMasterForm

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
    form = CodeMasterForm
    list_display = ['name', 'code', 'display_order', 'codecategory','start_date', 'end_date']
    list_filter = ['codecategory__name', 'start_date']
    search_fields = ('codecategory__name', 'name')
    date_hierarchy = 'start_date'


