from django import forms
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import FormView


class UploadView(FormView):
    class UploadForm(forms.Form):
        upload_file = forms.FileField(
            required=True,
            label = _('File to upload')
        )

    form_class = UploadForm
    template_name = "commndata/upload.html"


