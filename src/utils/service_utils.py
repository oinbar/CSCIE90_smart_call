import subprocess

def google_cloud_auth(key_file):
    cmd1 = "sudo gcloud auth activate-service-account --key-file=%s" % key_file
    cmd2 = "sudo gcloud auth print-access-token"
    access_token = subprocess.check_output(cmd1 + " && " + cmd2, shell=True)
    return access_token