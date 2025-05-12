"""
Django admin customisation
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""

    # Set the default order of users to be by their ID
    ordering = ['id']
    # Specify the fields to display in the list view: email and name
    list_display = ['email', 'name']

    # Define the layout and organisation of fields in the Django admin form
    # used to group fields into sections, making the form more organised and easier to navigate.
    # It is a tuple of tuples, where each inner tuple represents a section of the form.
    fieldsets = (
        # First section: 'email' and 'password' fields
        # (None, {'fields': ('email', 'password')}), # No header title for this section

        # '_()' is a standard Django utility for marking strings for translation,
        # allowing the label "User Details" to be translated into other languages if needed.
        (_('User Details'), {'fields': ('email', 'password')}),

        # Second section: 'Permissions' section
        (
            _('Permissions'),  # Section title, translatable
            {
                # Fields related to user permissions
                'fields': ('is_active', 'is_staff', 'is_superuser')
            }
        ),

        # Third section: 'Important dates' section
        # Shows the 'last_login' field
        (_('Important dates'), {'fields': ('last_login',)})
    )

    # Define which fields should be read-only in the admin interface
    # 'last_login' is read-only, as it's automatically set by Django
    readonly_fields = ['last_login']

    # Customise the form layout for adding a new user in the Django admin
    # Django knows that add_fieldsets is specifically for adding a user,
    # because it's part of the UserAdmin class configuration.
    # The UserAdmin class is a special Django admin class
    # that customises the user management interface in the Django admin panel.
    add_fieldsets = (
        (
            None, {  # No section title for this section
                # Apply 'wide' class for wider form fields
                'classes': ('wide',),
                'fields': (  # Fields to be displayed when adding a new user
                    'email',  # Email field
                    'password1',  # First password field
                    'password2',  # Second password field (for confirmation)
                    'name',  # User's full name
                    'is_active',  # Whether the user is active
                    'is_staff',  # Whether the user has staff privileges
                    'is_superuser',  # Whether the user has superuser privileges
                ),
            }
        ),
    )


"""
Register the custom UserAdmin to manage the 'User' model in the Django admin interface
admin.site.register(models.User, UserAdmin): This registers the User model with the custom UserAdmin class.
This tells Django to use UserAdmin to manage the display of User objects in the Django admin interface.
It ensures that when you view the user model in the admin, it follows the configuration defined in UserAdmin
"""
admin.site.register(models.User, UserAdmin)


admin.site.register(models.Recipe)
