from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
import os
import shutil
from django.conf import settings
import sys
DIRE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(DIRE, 'utils'))

# Lokasi folder upload
UPLOAD_FOLDER = "query-file/"

def clear_upload_folder(folder_path):
    """
    Bersihkan folder upload dari semua file.
    """
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)  # Hapus folder beserta isinya
    os.makedirs(folder_path, exist_ok=True)  # Buat ulang folder kosong

def save_uploaded_file(upload_folder, uploaded_file):
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, uploaded_file.name)
    with open(file_path, 'wb') as dest:
        for chunk in uploaded_file.chunks():
            dest.write(chunk)
    return file_path

def queryPage(request):
    """
    Halaman query utama.
    Menangani pengunggahan file audio atau gambar untuk melakukan pencarian.
    """
    if request.method == 'POST':
        # Bersihkan folder upload sebelum menyimpan file baru
        clear_upload_folder(UPLOAD_FOLDER)

        if 'query-audio' in request.FILES:
            # Proses file audio
            query_audio = request.FILES['query-audio']

            if query_audio.content_type not in ['audio/wav', 'audio/mid', 'audio/midi']:
                return HttpResponseBadRequest("Invalid audio file type.")
            
            audio_path = save_uploaded_file(UPLOAD_FOLDER, query_audio)
            print(f"Audio uploaded successfully: {audio_path}")

            # Jalankan proses pencarian audio
            all_similar_audio = querybyHumming(UPLOAD_FOLDER, settings.MEDIA_ROOT)

            # Paginasi hasil pencarian audio
            paginator = Paginator(all_similar_audio, 2)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            return render(request, 'query/queryPage.html', {
                'querying': True, 
                'image_true': False,
                'page_obj': page_obj,
                'query': query_audio.name,
            })

        elif 'query-image' in request.FILES:
            # Proses file gambar
            query_image = request.FILES['query-image']

            if query_image.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
                return HttpResponseBadRequest("Invalid image file type.")
            
            image_path = save_uploaded_file(UPLOAD_FOLDER, query_image)
            print(f"Image uploaded successfully: {image_path}")

            # Jalankan proses pencarian gambar
            all_similar_images = main(UPLOAD_FOLDER, settings.MEDIA_ROOT)

            # Paginasi hasil pencarian gambar
            paginator = Paginator(all_similar_images, 2)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            return render(request, 'query/queryPage.html', {
                'querying': True, 
                'image_true': True,
                'page_obj': page_obj,
                'query': query_image.name,
            })
        
        return HttpResponseBadRequest("No file uploaded.")

    # Jika metode GET, render halaman kosong
    return render(request, 'query/queryPage.html', {'querying': False})