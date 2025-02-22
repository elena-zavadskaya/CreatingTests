from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

from teachers import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/login/', permanent=True)),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('create-test/', views.create_test, name='create_test'),
    path('view-tests/', views.view_tests, name='view_tests'),
    path('edit-test/<int:test_id>/', views.edit_test, name='edit_test'),
    path('view-results/', views.view_results, name='view_results'),
    path('logout/', views.logout_view, name='logout'),
]
