from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.conf import settings
import os
import shutil
import time

from .QuerybyHumming import querybyHumming
from .image_process import main

UPLOAD_FOLDER = "query-file/"

def clear_upload_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path, exist_ok=True)

def save_uploaded_file(upload_folder, uploaded_file):
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, uploaded_file.name)
    with open(file_path, 'wb') as dest:
        for chunk in uploaded_file.chunks():
            dest.write(chunk)
    return file_path

def findJsonFile(folder_path):
    return [filename for filename in os.listdir(folder_path) 
            if filename.endswith(".json") 
            and not filename.startswith('.') 
            and not filename.startswith('._')]

def findAudioFile(folder_path):
    return [filename for filename in os.listdir(folder_path) 
            if filename.endswith((".wav", ".mid", ".midi")) 
            and not filename.startswith('.') 
            and not filename.startswith('._')]

def findImageFile(folder_path):
    return [filename for filename in os.listdir(folder_path) 
            if filename.endswith((".jpeg", ".jpg", ".png")) 
            and not filename.startswith('.') 
            and not filename.startswith('._')]

def queryPage(request):
    start_time = time.time()
    search_query = request.GET.get('search', '').strip()

    if request.method == 'GET' and (request.GET.get('page') or search_query):
        query_type = request.session.get('query_type', None)
        if query_type == 'audio':
            all_similar_results = request.session.get('audio_results', [])
            image_true = False
        elif query_type == 'image':
            all_similar_results = request.session.get('image_results', [])
            image_true = True
        else:
            return render(request, 'query/queryPage.html', {'querying': False})

        # Filter hasil berdasarkan pencarian
        if search_query:
            all_similar_results = [
                result for result in all_similar_results
                if search_query.lower() in result['Audio'].lower() or search_query.lower() in result['Composer'].lower()
            ]

    elif request.method == 'POST':
        clear_upload_folder(UPLOAD_FOLDER)

        if 'query-audio' in request.FILES:
            query_audio = request.FILES['query-audio']
            audio_path = save_uploaded_file(UPLOAD_FOLDER, query_audio)

            mapper_path = findJsonFile(settings.MEDIA_ROOT)
            audio_paths = findAudioFile(settings.MEDIA_ROOT)

            if mapper_path:
                # Get absolute path to uploads folder
                uploads_path = settings.MEDIA_ROOT
                all_similar_audio = querybyHumming(audio_path, audio_paths, mapper_path[0], uploads_path)
                request.session['query_type'] = 'audio'
                request.session['audio_results'] = all_similar_audio
                image_true = False
                all_similar_results = all_similar_audio
            else:
                return HttpResponseBadRequest("Mapper file not found.")

        elif 'query-image' in request.FILES:
            query_image = request.FILES['query-image']
            query_image_path = save_uploaded_file(UPLOAD_FOLDER, query_image)

            database_folder = settings.MEDIA_ROOT
            mapper_path = findJsonFile(settings.MEDIA_ROOT)

            if mapper_path:
                all_similar_image = main(query_image_path, database_folder, mapper_path, target_size=(70, 70))
                request.session['query_type'] = 'image'
                request.session['image_results'] = all_similar_image
                image_true = True
                all_similar_results = all_similar_image
            else:
                return HttpResponseBadRequest("Mapper file not found.")

    else:
        return render(request, 'query/queryPage.html', {'querying': False})

    paginator = Paginator(all_similar_results, 5)
    page_number = int(request.GET.get('page', 1))
    page_obj = paginator.get_page(page_number)

    # Pagination logic (max 7 pages)
    max_pages = 7
    current_page = page_obj.number
    total_pages = page_obj.paginator.num_pages
    start_page = max(1, current_page - 3)
    end_page = min(total_pages, start_page + max_pages - 1)

    if end_page - start_page < max_pages - 1:
        start_page = max(1, end_page - max_pages + 1)

    execution_time = (time.time() - start_time) * 1000

    return render(request, 'query/queryPage.html', {
        'querying': True,
        'image_true': image_true,
        'page_obj': page_obj,
        'search_query': search_query,
        'execution_time': execution_time,
        'pagination_range': range(start_page, end_page + 1),
    })
