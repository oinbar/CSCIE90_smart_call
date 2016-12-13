import base64
import urllib
import tempfile
import requests
import sys
import json
import subprocess
import argparse
from src.utils import audio_utils
from src.utils import service_utils
from src.utils import utils
import os
import time
from scipy.io.wavfile import read
from scipy.io.wavfile import write

# "https://cloud.google.com/speech/docs/getting-started"
key_file = utils.get_project_root() + "/src/credentials/google_cloud_key.json"
key_obj = json.loads(open(key_file).read())
proj_id = key_obj["project_id"]


def copy_file_to_google_storage_and_delete(f):
    subprocess.check_output(
        "sudo gsutil cp %s gs://%s.appspot.com/" % (f, proj_id),
        shell=True)
    os.remove(f)
    return "gs://%s.appspot.com/" + os.path.basename(f) % proj_id

def generate_speech_api_request_json(uri):
    request_json = {
          'config': {
              'encoding': 'LINEAR16',
              'sampleRate': 8000,
              'languageCode': 'en-US', # he-IL
              'maxAlternatives': 1,
              'speech_context': {
                  'phrases': []}
          },
          'audio': {
              'uri': uri
            }
        }
    return json.dumps(request_json)

def call_async_recognize(request_json, access_token):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + str(access_token).rstrip('\n'),
    }
    response = requests.post('https://speech.googleapis.com/v1beta1/speech:asyncrecognize',
        headers=headers, data=request_json, verify=False)
    operation_id = json.loads(response.content)["name"]
    return operation_id

def get_transcription_from_operation(operation_id, access_token, sleep_time=5):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + str(access_token).rstrip('\n'),
    }

    # keep checking if finished transcription
    result = {}
    waited = 0
    tries = 1
    while "done" not in result or str(result["done"])=="false":
        if tries > 1:
            time.sleep(sleep_time)
        response = requests.get(
            'https://speech.googleapis.com/v1beta1/operations/' + str(operation_id),
            headers=headers, verify=False)
        result = json.loads(response.content)
        waited += sleep_time
    print "waited % secs for transcription" % str(waited)
    return result

def send_audio_segments_to_async_recognize(channels, sampling_r, access_token):
    # get timestamped-intervals for both channels
    channels_operations_timestamps = {} # will hold all objects that are being transcribed by google asyncronously
    for i,channel in enumerate(channels):
        channels_operations_timestamps["channel"+str(i)] = {}
        data = read(channel)
        intervals = audio_utils.intervals_from_signal(data[1], sampling_r)
        for start,stop in intervals:
            f = tempfile.NamedTemporaryFile(delete=False, dir=utils.get_project_root() + "/data/tmp/").name
            write(f, sampling_r, data[1][start:stop])
            gs_url = copy_file_to_google_storage_and_delete(f)
            request_json = generate_speech_api_request_json(gs_url)
            operation_id = call_async_recognize(request_json, access_token)
            start_offset = start/float(sampling_r)
            stop_offset = stop/float(sampling_r)
            channels_operations_timestamps["channel"+str(i)][operation_id] = (start_offset, stop_offset)
    return channels_operations_timestamps

def collect_transcriptions_from_async_recognize(channels_operations_timestamps, access_token):
    results = {"results": {}}
    for channel in channels_operations_timestamps.keys():
        results["results"][channel] = []
        for opid in channels_operations_timestamps[channel]:
            transcription = get_transcription_from_operation(opid, access_token)
            time_offset = channels_operations_timestamps[channel][opid]
            results["results"][channel].append({
                "time_offset":time_offset,
                "transcription":transcription})
    return results


def transcribe_audio_url(recording_url):
    # moves the audio file to google cloud so application can access the uri directly. application sends async request
    # for transcription of uri. limited to 80 minutes of audio. performs this on segmented audio chunks, by first
    # sending them all to the service, and then collecting the results in a second step
    access_token = service_utils.google_cloud_auth(key_file)
    f = utils.download_recording(recording_url)
    analysis = audio_utils.analyze_wave_file(f)
    if analysis["nChannels"]==2:
        f1, f2 = audio_utils.split_wav_file(f)
        channels_operations_timestamps = send_audio_segments_to_async_recognize(
            [f1, f2], analysis["frameRate"], access_token)
        results = collect_transcriptions_from_async_recognize(channels_operations_timestamps, access_token)
        results["recording_url"] = recording_url
        return results

    else:
        gs_url = copy_file_to_google_storage_and_delete(f)
        request_json = generate_speech_api_request_json(gs_url)
        operation_id = call_async_recognize(request_json, access_token)
        transcription = get_transcription_from_operation(operation_id, access_token)
        return {"results": transcription, "recording_url": recording_url}


# TODO delete files on google when done


parser = argparse.ArgumentParser()
parser.add_argument("-url", type=str, required=True, help="recording url")

if __name__ == "__main__":
    args = parser.parse_args()
    transcription = transcribe_audio_url(args.url)
    print json.dumps(transcription, ensure_ascii=False)

