from django.contrib import admin
from django.urls import path, include
from .import views

urlpatterns = [
path('', views.get_projects, name='view_all_projects'),
path('signup', views.signup, name='signup'),
path('activate/<uidb64>/<token>', views.activate, name='activate'),
path('signin', views.signin, name='signin'),
path('signout', views.signout, name='signout'),
path('create/', views.create_project, name='create_project'),
path('get/', views.get_projects, name='view_all_projects'),
path('filter/', views.filter_projects, name='project_detail'),
path('get/<int:id>', views.retrieve_projects, name='retrieve_projects'),
path('update/<int:id>', views.update_project, name='update_project'),
path('delete/<int:id>', views.delete_project, name='delete'),
# path('profile/', views.profile, name='profile')
]
