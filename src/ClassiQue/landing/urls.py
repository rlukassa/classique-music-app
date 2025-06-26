from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include  # Tambahkan `include` di sini
from . import views

urlpatterns = [
    path("", views.home, name="home"),  # Halaman utama
    path("upload/", views.uploadPage, name="uploadPage"),  # Halaman upload
    path("upload/clear/", views.clear_uploads, name="clear_uploads"),  # Clear uploads endpoint
    path("upload/load-demo/", views.load_demo_data, name="load_demo_data"),  # Load demo data endpoint
    path("dataView/", views.dataView, name="dataView"),  # Halaman data view
    path("query/", include("query.urls")),  # Aplikasi query
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
