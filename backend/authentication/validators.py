import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class PasswordComplexityValidator:
    """
    Custom password validator that enforces password complexity requirements:
    - Minimum 8 characters
    - At least 1 uppercase letter
    - At least 1 special character
    """

    def validate(self, password, user=None):
        """
        Validate that the password meets complexity requirements.
        
        Args:
            password: The password string to validate
            user: The user object (optional, not used in this validator)
            
        Raises:
            ValidationError: If password doesn't meet requirements
        """
        errors = []

        # Check minimum length (8 characters)
        if len(password) < 8:
            errors.append(_("Password must contain at least 8 characters."))

        # Check for at least 1 uppercase letter
        if not re.search(r'[A-Z]', password):
            errors.append(_("Password must contain at least 1 uppercase letter."))

        # Check for at least 1 special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/;\'`~]', password):
            errors.append(_("Password must contain at least 1 special character."))

        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        """
        Return a help text describing the password requirements.
        """
        return _(
            "Your password must contain at least 8 characters, "
            "including at least 1 uppercase letter and 1 special character."
        )
