from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, LDAPConfiguration, WebLogin


@admin.register(LDAPConfiguration)
class LDAPConfigurationAdmin(admin.ModelAdmin):
    list_display = ['ConnectionName', 'HostName', 'Port', 'BaseDN', 'UseSSL', 'Active']
    list_filter = ['Active', 'UseSSL', 'UseTLS']
    search_fields = ['ConnectionName', 'HostName', 'BaseDN']
    readonly_fields = ['CreatedAt', 'UpdatedAt']
    
    fieldsets = (
        ('Basic Configuration', {
            'fields': ('ConnectionName', 'HostName', 'Port', 'Active')
        }),
        ('LDAP Settings', {
            'fields': ('BaseDN', 'BindDN', 'BindPassword', 'UserSearchBase', 'UserSearchFilter')
        }),
        ('Security', {
            'fields': ('UseSSL', 'UseTLS')
        }),
        ('Timestamps', {
            'fields': ('CreatedAt', 'UpdatedAt')
        }),
    )


@admin.register(WebLogin)
class WebLoginAdmin(admin.ModelAdmin):
    list_display = ['UserId', 'UserName', 'AuthMode', 'Active', 'LastLogin']
    list_filter = ['AuthMode', 'Active']
    search_fields = ['UserId', 'UserName', 'Email']
    readonly_fields = ['CreatedAt', 'UpdatedAt', 'LastLogin']
    
    fieldsets = (
        ('User Information', {
            'fields': ('UserId', 'UserName', 'Email', 'Department')
        }),
        ('Authentication', {
            'fields': ('AuthMode', 'Pwd', 'Active')
        }),
        ('Timestamps', {
            'fields': ('CreatedAt', 'UpdatedAt', 'LastLogin')
        }),
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'status', 'is_ldap_user', 'is_active', 'last_seen']
    list_filter = ['status', 'is_ldap_user', 'is_active', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-last_seen']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('status', 'status_message', 'profile_picture', 'phone_number', 'department', 'section', 'is_ldap_user')
        }),
    )
