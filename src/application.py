from flask import Flask, request
import twilio.twiml
import os
import json
from src.utils import utils
import datetime
from datetime import timedelta

app = Flask(__name__)

@app.route("/test", methods=['GET', 'POST'])
def app_test():
    """Respond to incoming requests."""
    resp = twilio.twiml.Response()
    resp.say("successful twilio connection")
    return str(resp)

@app.route("/record", methods=['GET', 'POST'])
def record():
    # record phone call
    resp = twilio.twiml.Response()
    resp.record(timeout=20, action="/handle-recording")
    return str(resp)

@app.route("/get-number-to-call", methods=['GET', 'POST'])
def get_num_to_call():
    # call new person and record
    resp = twilio.twiml.Response()
    resp.gather(timeout="15", finishOnKey="*", action="/call-and-record")\
        .say("Please dial the full number you wish to reach. At the end, press star.")
    return str(resp)

@app.route("/call-and-record", methods=['GET', 'POST'])
def call_and_record():
    digits = request.values.get('Digits', None)
    resp = twilio.twiml.Response()
    resp.dial(digits, timeout=20, action="/handle-recording/call/%s" % digits,
              record="record-from-answer-dual")
    return str(resp)

@app.route("/handle-recording/call/<digits>", methods=['GET', 'POST'])
def handle_recording(digits):
    # grabs recording url, and saves url to file along with some metadata
    # TODO file download should be done asynchronously
    recording_url = request.values.get("RecordingUrl", None)
    duration_secs = request.values.get("RecordingDuration", None)
    from_number = request.values.get('From', None)

    timestamp = datetime.datetime.now() - timedelta(seconds=int(duration_secs))
    timestamp = timestamp.isoformat()

    data = json.dumps({"from": from_number,
                       "to": str(digits),
                       "recording_url": recording_url,
                       "timestamp": timestamp}, ensure_ascii=False)
    fname = utils.get_project_root() + \
            "/data/raw/%s%s%s.txt" % (str(timestamp), "|",  str(from_number))
    with open(fname, "w") as f:
        f.write(data)

    resp = twilio.twiml.Response()
    resp.say("Call recorded successfully")
    return str(resp)




if __name__ == "__main__":
	# workaround since pid file check if process is running is not working
	app.run(host=os.getenv('LISTEN', '0.0.0.0'), port=int(os.getenv('PORT', '5000')))
