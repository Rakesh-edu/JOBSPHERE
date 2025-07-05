from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('home/', views.base, name='home'),
    path('',views.register,name='register'),
    path('login/',views.login,name='login'),
    path('profile/',views.profile,name='profile'),
    path('recruiters-dashboard/',views.rdashboard,name='rdashboard'),
    path('jobs/',views.jobs,name='jobs'),
    path('campany/',views.company,name='company'),
    path('udashboard/',views.udashboard,name='udashboard'),
    path('rhome/', views.rhome, name='rhome'),
    path('rdashboard/',views.rdashboard,name='rdashboard'),
    path('postjob/',views.postjob,name='postjob'),
    path('applicants/',views.applicants,name='applicants'),
    path('rprofile/',views.rprofile,name='rprofile'),
    path('apply/<int:job_id>/',views.apply_to_job,name='apply_to_job'),
    path('job/<int:job_id>/', views.job_details, name='job_details'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)