import os
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import shutil

# Create your views here.

def home(request): # Landing page
    return render(request, "landing/home.html")

def uploadPage(request): # Path menuju halaman upload datasets
    if request.method == 'POST':
        # 1. Proses dataset audio
        audio_files = request.FILES.getlist('audio-dataset')  # Input audio
        if audio_files:
            folder_audio = os.path.join(settings.MEDIA_ROOT, 'audio')
            os.makedirs(folder_audio, exist_ok=True)
            for file in audio_files:
                fs = FileSystemStorage(location=folder_audio)
                saved_path = fs.save(file.name, file)
                print(f"Audio file saved to: {os.path.join(folder_audio, saved_path)}")

        # 2. Proses dataset gambar
        image_files = request.FILES.getlist('image-dataset')  # Input gambar
        if image_files:
            folder_image = os.path.join(settings.MEDIA_ROOT, 'images')
            os.makedirs(folder_image, exist_ok=True)
            for file in image_files:
                fs = FileSystemStorage(location=folder_image)
                saved_path = fs.save(file.name, file)
                print(f"Image file saved to: {os.path.join(folder_image, saved_path)}")

        # 3. Proses file mapper
        mapper_file = request.FILES.get('mapper-data')  # Input mapper
        if mapper_file:
            folder_mapper = os.path.join(settings.MEDIA_ROOT, 'mapper')
            os.makedirs(folder_mapper, exist_ok=True)
            fs = FileSystemStorage(location=folder_mapper)
            saved_path = fs.save(mapper_file.name, mapper_file)
            print(f"Mapper file saved to: {os.path.join(folder_mapper, saved_path)}")

        return render(request, "query/queryPage.html")
    return render(request, "landing/uploadPage.html")

def clear_folder(folder_path):
    """
    Hapus semua isi folder (file dan subfolder).
    """
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)  # Hapus folder beserta isinya
    os.makedirs(folder_path, exist_ok=True)  # Buat folder baru kosong

def uploadPage(request):  # Path menuju halaman upload datasets
    if request.method == 'POST':
        # 1. Proses dataset audio
        audio_files = request.FILES.getlist('audio-dataset')  # Input audio
        if audio_files:
            folder_audio = os.path.join(settings.MEDIA_ROOT, 'audio')
            clear_folder(folder_audio)  # Bersihkan folder audio
            for file in audio_files:
                fs = FileSystemStorage(location=folder_audio)
                saved_path = fs.save(file.name, file)
                print(f"Audio file saved to: {os.path.join(folder_audio, saved_path)}")

        # 2. Proses dataset gambar
        image_files = request.FILES.getlist('image-dataset')  # Input gambar
        if image_files:
            folder_image = os.path.join(settings.MEDIA_ROOT, 'images')
            clear_folder(folder_image)  # Bersihkan folder gambar
            for file in image_files:
                fs = FileSystemStorage(location=folder_image)
                saved_path = fs.save(file.name, file)
                print(f"Image file saved to: {os.path.join(folder_image, saved_path)}")

        # 3. Proses file mapper
        mapper_file = request.FILES.get('mapper-data')  # Input mapper
        if mapper_file:
            folder_mapper = os.path.join(settings.MEDIA_ROOT, 'mapper')
            clear_folder(folder_mapper)  # Bersihkan folder mapper
            fs = FileSystemStorage(location=folder_mapper)
            saved_path = fs.save(mapper_file.name, mapper_file)
            print(f"Mapper file saved to: {os.path.join(folder_mapper, saved_path)}")

        return render(request, "query/queryPage.html")
    return render(request, "landing/uploadPage.html")