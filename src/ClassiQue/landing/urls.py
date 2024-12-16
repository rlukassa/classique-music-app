from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('upload/', views.uploadPage, name='uploadPage'),
    path('dataView/', views.dataView, name='dataView'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)