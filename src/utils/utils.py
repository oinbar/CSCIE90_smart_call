import os
import urllib
import tempfile

def get_project_root(identifier=".git"):
    dir = os.path.dirname(os.path.abspath(__file__))
    while identifier not in os.listdir(dir):
        # climb one dir up
        dir = os.path.abspath(os.path.join(dir, os.pardir))
    return dir

def download_recording(recording_url):
    f = tempfile.NamedTemporaryFile(delete=False, dir=get_project_root() + "/data/tmp/")
    urllib.urlretrieve(recording_url, f.name)
    return f.name