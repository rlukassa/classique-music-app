import os
import shutil
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest

# Lokasi folder upload
UPLOAD_FOLDER = "query-file/"

def clear_upload_folder(folder_path):
    """
    Bersihkan folder upload dari semua file.
    """
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)  # Hapus folder beserta isinya
    os.makedirs(folder_path, exist_ok=True)  # Buat ulang folder kosong

def queryPage(request):
    """
    Halaman query utama.
    Menangani pengunggahan file audio atau gambar untuk melakukan pencarian.
    """
    if request.method == 'POST':
        # Bersihkan folder upload sebelum menyimpan file baru
        clear_upload_folder(UPLOAD_FOLDER)
        
        # Variabel untuk menyimpan hasil proses upload
        responses = []
        
        # Handle file audio
        if 'query-audio' in request.FILES:
            query_audio = request.FILES['query-audio']
            if query_audio.content_type in ['audio/wav', 'audio/mid', 'audio/midi']:
                audio_dir = os.path.join(UPLOAD_FOLDER)
                os.makedirs(audio_dir, exist_ok=True)
                
                audio_path = os.path.join(audio_dir, query_audio.name)
                with open(audio_path, 'wb') as audio_file:
                    for chunk in query_audio.chunks():
                        audio_file.write(chunk)
                
                responses.append(f"Audio uploaded successfully: {audio_path}")
            else:
                responses.append("Invalid audio file type.")
        
        # Handle file image
        elif 'query-image' in request.FILES:
            query_image = request.FILES['query-image']
            if query_image.content_type in ['image/jpeg', 'image/png']:
                image_dir = os.path.join(UPLOAD_FOLDER)
                os.makedirs(image_dir, exist_ok=True)
                
                image_path = os.path.join(image_dir, query_image.name)
                with open(image_path, 'wb') as image_file:
                    for chunk in query_image.chunks():
                        image_file.write(chunk)
                
                responses.append(f"Image uploaded successfully: {image_path}")
            else:
                responses.append("Invalid image file type.")
        
        # Jika tidak ada file yang valid
        if not responses:
            return HttpResponseBadRequest("No valid files uploaded.")
        
        # Kirimkan hasil proses file
        return HttpResponse("<br>".join(responses))
    
    # Jika GET, render halaman template
    return render(request, 'query/queryPage.html')
