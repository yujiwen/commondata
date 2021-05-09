from commndata.forms import BaseTableForm
from commndata.models import CodeMaster

class CodeMasterForm(BaseTableForm):
    class Meta:
        model = CodeMaster
        