from django.contrib import admin

from account.models.base import CustomUser, Organization, Otp, OrganizationInvite, Payment


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'phone_number', 'first_name', 'last_name', 'verified_email', 'verified_phone']
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['uuid']

    def save_model(self, request, obj, form, change):
        # Hash the password on creating new user:
        if not obj.pk:
            obj.set_password(form.cleaned_data['password'])
            obj.save()
        super().save_model(request, obj, form, change)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'balance']
    readonly_fields = ['uuid']


@admin.register(Otp)
class OtpAdmin(admin.ModelAdmin):
    list_display = ['user']
    readonly_fields = ['uuid']


@admin.register(OrganizationInvite)
class OrganizationInviteAdmin(admin.ModelAdmin):
    list_display = ['organization', 'email', 'status']
    readonly_fields = ['uuid']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['organization', 'user', 'amount', 'status']
    readonly_fields = ['uuid']
