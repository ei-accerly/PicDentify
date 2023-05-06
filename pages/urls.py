from django.urls import path
from . import views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static
app_name = 'pages'

urlpatterns = [
    path('', views.LoginPage.as_view(), name='login'),
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
    path('dashboard', views.Dashboard.as_view(), name='dashboard'),
    path('dashboard/mytopic', views.TopicPage.as_view(), name='topicpage'),
    path('studentdashboard/', views.StudentDashboard.as_view(), name='studentdashboard'),
    path('studentdashboard/studentactivity/', views.StudentActivity.as_view(), name='studentactivity'),
    path('studentdashboard/studentactivity', views.StudentActivity.as_view(), name='studentactivity'),
    path('try/', views.TryView.as_view(), name='try'),
    path('logout_view/', views.logout_view, name='logout_view'),
    path('logout_view', views.logout_view, name='logout_view'),
    path('studentlogin/', views.StudentLogin.as_view(), name='studentlogin'),
    path('studentlogin', views.StudentLogin.as_view(), name='studentlogin'),
    
]
