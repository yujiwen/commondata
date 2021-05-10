from django.contrib.admin.forms import AdminAuthenticationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm

class SuperUserAuthenticationForm(AdminAuthenticationForm):
    """
    superuserのみ認証可能
    """
    error_messages = {
        **AdminAuthenticationForm.error_messages,
        'invalid_login': _(
            "Please enter the correct %(username)s and password for a superuser "
            "account. Note that both fields may be case-sensitive."
        ),
    }
    required_css_class = 'required'

    def confirm_login_allowed(self, user):
        super(SuperUserAuthenticationForm, self).confirm_login_allowed(user)
        if not user.is_superuser:
            raise ValidationError(
                self.error_messages['invalid_login'],
                code='invalid_login',
                params={'username': self.username_field.verbose_name}
            )

class ActiveUserAuthenticationForm(AuthenticationForm):
    """
    AdminAuthenticationFormにてのuser.is_staffチェックを回避し、user.is_activeのみチェックする
    """
    def confirm_login_allowed(self, user):
        super(ActiveUserAuthenticationForm, self).confirm_login_allowed(user)

class BaseTableForm(ModelForm):
    error_messages = {
        'invalid_period': _(
            'The %(end_date)s must be newer then %(start_date)s.'
        ),
    }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and start_date > end_date:
            # opts = self._meta.model._meta
            end_label = self.fields['end_date'].label
            start_label = self.fields['start_date'].label
            raise ValidationError(
                self.error_messages['invalid_period'],
                code='invalid_period',
                params = {'end_date': end_label, 'start_date': start_label}
            )