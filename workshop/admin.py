from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Workbench, UserWorkbench, Card, Step, Element


class UserCreationForm(forms.ModelForm):
    type = forms.CharField(label='user type')
    organization = forms.CharField(label='user organization')
    phone = forms.IntegerField(label='user phone')
    position = forms.CharField(label='user position')

    class Meta:
        model = User
        fields = ('type',)

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    list_display = ('username', 'email', 'type', 'organization', 'position')
    fieldsets = (
        (None, {'fields': ('username', 'password', 'email')}),
        ('Personal info', {'fields': ('type', 'organization', 'phone', 'position', 'is_staff')}),
        ('Permissions', {'fields': ('is_superuser',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password', 'email', 'type', 'organization', 'phone', 'position', 'is_staff'),
        }),
    )


class WorkshopAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_by', 'created_at')


class WorkbenchAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at')


class CardAdmin(admin.ModelAdmin):
    list_display = ('name', 'sup_type', 'type', 'description')


class StepAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'workbench', 'order')


class StickerAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'content', 'step', 'card', 'created_by')


admin.site.register(User, UserAdmin)
admin.site.register(Workbench, WorkbenchAdmin)
admin.site.register(UserWorkbench)
admin.site.register(Card, CardAdmin)
admin.site.register(Step, StepAdmin)
admin.site.register(Element, StickerAdmin)
