import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import FileSystemStorage
import shutil
import json
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.decorators.http import require_http_methods

# Create your views here.

def home(request):  # Landing page
    return render(request, "landing/home.html")

def get_file_counts():
    """
    Get counts of different file types in the uploads folder.
    """
    uploads_path = settings.MEDIA_ROOT
    audio_count = 0
    image_count = 0
    mapper_count = 0
    
    if os.path.exists(uploads_path):
        for filename in os.listdir(uploads_path):
            if filename.lower().endswith(('.mid', '.midi')):
                audio_count += 1
            elif filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_count += 1
            elif filename.lower().endswith('.json'):
                mapper_count += 1
    
    return {
        'audio_count': audio_count,
        'image_count': image_count,
        'mapper_count': mapper_count,
        'total_count': audio_count + image_count + mapper_count
    }

def clear_folder(folder_path):
    """
    Clear all contents of a folder (files and subfolders).
    """
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

@require_http_methods(["POST"])
def clear_uploads(request):
    """
    AJAX endpoint to clear all uploads.
    """
    try:
        clear_folder(settings.MEDIA_ROOT)
        return JsonResponse({
            'success': True, 
            'message': 'All uploads cleared successfully!',
            'file_counts': get_file_counts()
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'Error clearing uploads: {str(e)}'
        })

@require_http_methods(["POST"])
def load_demo_data(request):
    """
    AJAX endpoint to load demo data from demo folder to uploads folder.
    """
    try:
        # Get paths
        demo_path = os.path.join(settings.BASE_DIR, 'demo')
        uploads_path = settings.MEDIA_ROOT
        
        # Check if demo folder exists
        if not os.path.exists(demo_path):
            return JsonResponse({
                'success': False, 
                'message': 'Demo folder not found. Please contact the administrator.'
            })
        
        # Create uploads folder if it doesn't exist
        os.makedirs(uploads_path, exist_ok=True)
        
        # Clear existing uploads first
        clear_folder(uploads_path)
        
        # Copy all files from demo subfolders to uploads
        demo_audio_path = os.path.join(demo_path, 'audio')
        demo_image_path = os.path.join(demo_path, 'image')
        demo_mapper_path = os.path.join(demo_path, 'mapper.json')
        
        files_copied = 0
        
        # Copy audio files
        if os.path.exists(demo_audio_path):
            for filename in os.listdir(demo_audio_path):
                if filename.lower().endswith(('.mid', '.midi')):
                    source = os.path.join(demo_audio_path, filename)
                    destination = os.path.join(uploads_path, filename)
                    shutil.copy2(source, destination)
                    files_copied += 1
        
        # Copy image files
        if os.path.exists(demo_image_path):
            for filename in os.listdir(demo_image_path):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    source = os.path.join(demo_image_path, filename)
                    destination = os.path.join(uploads_path, filename)
                    shutil.copy2(source, destination)
                    files_copied += 1
        
        # Copy mapper file
        if os.path.exists(demo_mapper_path):
            destination = os.path.join(uploads_path, 'mapper.json')
            shutil.copy2(demo_mapper_path, destination)
            files_copied += 1
        
        # Get updated file counts
        file_counts = get_file_counts()
        
        return JsonResponse({
            'success': True, 
            'message': f'Demo dataset loaded successfully! {files_copied} files copied.',
            'file_counts': file_counts
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'Error loading demo data: {str(e)}'
        })

def uploadPage(request):  # Path menuju halaman upload datasets
    if request.method == 'POST':
        errors = []
        success_messages = []
        
        # 1. Process audio dataset
        audio_files = request.FILES.getlist('audio-dataset')
        if audio_files:
            folder_audio = os.path.join(settings.MEDIA_ROOT)
            os.makedirs(folder_audio, exist_ok=True)
            audio_count = 0
            for file in audio_files:
                if file.name.lower().endswith(('.mid', '.midi')):
                    fs = FileSystemStorage(location=folder_audio)
                    saved_path = fs.save(file.name, file)
                    audio_count += 1
                else:
                    errors.append(f"Audio file '{file.name}' is not a valid MIDI file.")
            if audio_count > 0:
                success_messages.append(f"Successfully uploaded {audio_count} audio file(s).")

        # 2. Process image dataset
        image_files = request.FILES.getlist('image-dataset')
        if image_files:
            folder_image = os.path.join(settings.MEDIA_ROOT)
            os.makedirs(folder_image, exist_ok=True)
            image_count = 0
            for file in image_files:
                if file.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                    fs = FileSystemStorage(location=folder_image)
                    saved_path = fs.save(file.name, file)
                    image_count += 1
                else:
                    errors.append(f"Image file '{file.name}' is not a valid image format.")
            if image_count > 0:
                success_messages.append(f"Successfully uploaded {image_count} image file(s).")

        # 3. Process mapper file
        mapper_file = request.FILES.get('mapper-data')
        if mapper_file:
            if mapper_file.name.lower().endswith('.json'):
                folder_mapper = os.path.join(settings.MEDIA_ROOT)
                os.makedirs(folder_mapper, exist_ok=True)
                fs = FileSystemStorage(location=folder_mapper)
                saved_path = fs.save(mapper_file.name, mapper_file)
                success_messages.append("Successfully uploaded mapper file.")
            else:
                errors.append("Mapper file must be a JSON file.")

        # Validation: Check if all required files are present
        file_counts = get_file_counts()
        if file_counts['audio_count'] == 0:
            errors.append("At least one audio file is required.")
        if file_counts['image_count'] == 0:
            errors.append("At least one image file is required.")
        if file_counts['mapper_count'] == 0:
            errors.append("A mapper JSON file is required.")

        # Add messages to display
        for error in errors:
            messages.error(request, error)
        for success in success_messages:
            messages.success(request, success)

        if not errors:
            messages.success(request, "All files uploaded successfully! You can now view your dataset.")
            return redirect('dataView')
    
    # Get current file counts for display
    file_counts = get_file_counts()
    return render(request, "landing/uploadPage.html", {'file_counts': file_counts})

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
