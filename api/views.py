from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.files.storage import default_storage
import os
import json
import torch
import audiofile
from uvr import models
from uvr.utils.get_models import download_all_models
import uuid
from threading import Thread
import time

models_json_path = "../models.json"
models_json = json.load(open(models_json_path, "r"))
download_all_models(models_json)
device = "cuda" if torch.cuda.is_available() else "cpu"

# In-memory status tracker
status_tracker = {
    "current_status": "no process",
    "job_id": None,
    "response_data": None
}

def use_vocal_remover(file_path):
    demucs = models.Demucs(name="hdemucs_mmi", other_metadata={
                           "segment": 2, "split": True}, device=device, logger=None)
    res = demucs(file_path)
    separated_audio = res
    return separated_audio

def process_music_file(file_path, job_id):
    try:
        status_tracker["current_status"] = "ongoing process"
        # Process the music file
        separated_audio = use_vocal_remover(file_path)

        # Save separated audio files and construct response data
        response_data = {}
        for part, audio_data in separated_audio.items():
            output_path = f"{file_path}_{part}.wav"
            audiofile.write(output_path, audio_data, 44100)
            response_data[part] = default_storage.url(output_path)

        # Clean up the uploaded file
        os.remove(file_path)

        status_tracker["response_data"] = response_data
        status_tracker["current_status"] = "no process"
        status_tracker["job_id"] = None
    except Exception as e:
        status_tracker["response_data"] = {'error': str(e)}
        status_tracker["current_status"] = "no process"
        status_tracker["job_id"] = None

@api_view(['POST'])
def process_music(request):
    if request.method == 'POST':
        music_file = request.FILES['mp']
        file_path = default_storage.save(music_file.name, music_file)
        job_id = str(uuid.uuid4())

        # Start the processing in a separate thread
        thread = Thread(target=process_music_file, args=(file_path, job_id))
        thread.start()

        status_tracker["current_status"] = "ongoing process"
        status_tracker["job_id"] = job_id
        status_tracker["response_data"] = None

        return Response({'job_id': job_id})

    return Response({'error': 'Invalid request method'}, status=400)

@api_view(['GET'])
def check_status(request):
    if status_tracker["job_id"] is None:
        return Response({'status': 'no process'})
    
    return Response({
        'status': status_tracker["current_status"],
        'response_data': status_tracker["response_data"]
    })
