from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Profile, UserFollowship

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'phone_number', 'email' ]
    fieldsets = [
        *UserAdmin.fieldsets,
    ]
    fieldsets.insert(
        2,
        (
            "Profile Information",
            {
                "fields": (   
                    "activation_otp", 
                    "phone_number", 
                ),
            },
        ),
    )

admin.site.register(CustomUser, CustomUserAdmin)

admin.site.register(Profile)
admin.site.register(UserFollowship)