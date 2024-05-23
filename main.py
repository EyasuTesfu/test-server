import sys

import uvr
from uvr import models
from uvr.utils.get_models import download_all_models
import torch
import audiofile
import json

models_json = json.load(
    open("./models.json", "r"))
download_all_models(models_json)
name = '1.wav'
device = "cpu"
print(device)

demucs = models.Demucs(name="hdemucs_mmi", other_metadata={
                       "segment": 2, "split": True}, device=device, logger=None)

print('demucs')
# Separating an audio file
res = demucs(name)
print('res')
seperted_audio = res
vocals = seperted_audio["vocals"]
base = seperted_audio["bass"]
drums = seperted_audio["drums"]
other = seperted_audio["other"]
vocals_path = "vocals.mp3"
base_path = "base.mp3"
drums_path = "drums.mp3"
other_path = "other.mp3"
print('generated')
audiofile.write(vocals_path, vocals, demucs.sample_rate)
audiofile.write(base_path, base, demucs.sample_rate)
audiofile.write(drums_path, drums, demucs.sample_rate)
audiofile.write(other_path, other, demucs.sample_rate)
