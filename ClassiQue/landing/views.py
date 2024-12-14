import os
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage

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