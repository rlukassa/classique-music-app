import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import shutil
import json
from django.core.paginator import Paginator

# Create your views here.

def home(request):  # Landing page
    return render(request, "landing/home.html")

def clear_folder(folder_path):
    """
    Hapus semua isi folder (file dan subfolder).
    """
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)  # Hapus folder beserta isinya
    os.makedirs(folder_path, exist_ok=True)  # Buat folder baru kosong

def uploadPage(request):  # Path menuju halaman upload datasets
    if request.method == 'POST':
        clear_folder(settings.MEDIA_ROOT)  # Bersihkan folder MEDIA_ROOT
        # 1. Proses dataset audio
        audio_files = request.FILES.getlist('audio-dataset')  # Input audio
        if audio_files:
            folder_audio = os.path.join(settings.MEDIA_ROOT)
            for file in audio_files:
                fs = FileSystemStorage(location=folder_audio)
                saved_path = fs.save(file.name, file)
                print(f"Audio file saved to: {os.path.join(folder_audio, saved_path)}")

        # 2. Proses dataset gambar
        image_files = request.FILES.getlist('image-dataset')  # Input gambar
        if image_files:
            folder_image = os.path.join(settings.MEDIA_ROOT)
            for file in image_files:
                fs = FileSystemStorage(location=folder_image)
                saved_path = fs.save(file.name, file)
                print(f"Image file saved to: {os.path.join(folder_image, saved_path)}")

        # 3. Proses file mapper
        mapper_file = request.FILES.get('mapper-data')  # Input mapper
        if mapper_file:
            folder_mapper = os.path.join(settings.MEDIA_ROOT)
            fs = FileSystemStorage(location=folder_mapper)
            saved_path = fs.save(mapper_file.name, mapper_file)
            print(f"Mapper file saved to: {os.path.join(folder_mapper, saved_path)}")

        return redirect('dataView')
    return render(request, "landing/uploadPage.html")

def dataView(request):
    # Path ke file JSON mapper
    mapper_file_path = os.path.join(settings.MEDIA_ROOT, 'mapper.json')
    data = []

    # Load data dari file JSON
    if os.path.exists(mapper_file_path):
        with open(mapper_file_path, 'r') as f:
            json_data = json.load(f)
            data = json_data

    # Ambil query pencarian dari URL
    query = request.GET.get('search', '').lower()  # Ambil parameter 'search' (default kosong)

    # Filter data berdasarkan pencarian
    if query:
        data = [item for item in data if query in item.get('composer', '').lower()]

    # Paginator untuk membagi data ke dalam 8 item per halaman
    paginator = Paginator(data, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "landing/dataView.html", {
        'page_obj': page_obj,
        'MEDIA_URL': '/uploads/',
        'query': query  # Kirim query kembali ke template
    })
