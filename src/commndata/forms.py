from django.contrib.admin.forms import AdminAuthenticationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class SuperUserAuthenticationForm(AdminAuthenticationForm):
    """
    superuserのみ認証可能
    """
    error_messages = {
        **AuthenticationForm.error_messages,
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
    AdminAuthenticationFormにてuser.is_staffチェックを回避し、user.is_activeのみチェックする
    """
    def confirm_login_allowed(self, user):
        super(ActiveUserAuthenticationForm, self).confirm_login_allowed(user)

