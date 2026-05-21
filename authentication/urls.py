from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.ldap_login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.user_profile, name='profile'),
    path('users/', views.all_users, name='all_users'),
    path('status/', views.update_status, name='update_status'),
    path('logout/', views.logout_view, name='logout'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('fetch-employee/', views.fetch_employee_details, name='fetch_employee_details'),
    path('get-employee-details/', views.get_employee_details, name='get_employee_details'),
    path('test-db/', views.test_database_connection, name='test_database_connection'),
    path('test-mock/', views.test_mock_data, name='test_mock_data'),
    path('test-tables/', views.test_database_tables, name='test_database_tables'),
]
