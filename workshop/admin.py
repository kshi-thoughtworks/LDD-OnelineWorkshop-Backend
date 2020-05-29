from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Workshop, Workbench, UserWorkbench


class UserCreationForm(forms.ModelForm):
    wechat_id = forms.IntegerField(label='wechat id')
    type = forms.CharField(label='user type')
    organization = forms.CharField(label='user organization')
    phone = forms.IntegerField(label='user phone')
    position = forms.CharField(label='user position')

    class Meta:
        model = User
        fields = ('wechat_id', 'type')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.wechat_id = self.wechat_id
        if commit:
            user.save()
        return user


class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    list_display = ('username', 'type', 'organization', 'phone', 'position')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('wechat_id', 'type', 'organization', 'phone', 'position', 'is_staff')}),
        ('Permissions', {'fields': ('is_superuser',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password', 'wechat_id', 'type', 'organization', 'phone', 'position'),
        }),
    )


admin.site.register(User, UserAdmin)
admin.site.register(Workshop)
admin.site.register(Workbench)
admin.site.register(UserWorkbench)
