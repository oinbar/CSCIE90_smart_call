import argparse
import json
from dateutil.parser import parse
from datetime import timedelta
import traceback
import sys

# parse speaker, timestamp, and transcripts, and leave out metadata
def create_convo_rows_from_multi_channel_transcript(results_dict):
    # [[channel, timestamp, [(transcript_alternative1, score), (transcript_alternative2, score)]]

    results = []
    for chan in results_dict["transcript"]["results"].keys():
        channel = results_dict["transcript"]["results"][chan]

        for transcription in channel:
            time_offset = transcription["time_offset"]
            if "results" in transcription["transcription"]["response"].keys():
                alternatives = transcription["transcription"]["response"]["results"][0]["alternatives"]
                alternatives = [(a["transcript"], a["confidence"]) for a in alternatives]
                alternatives = sorted(alternatives, key=lambda x: x[1], reverse=True)  # sorted by score

                results.append([chan, time_offset, alternatives])

    # sort results by timestamp
    results = sorted(results, key=lambda x: float(x[1][0]), reverse=False)
    return results

# method to compute actual time from offset
def offset_to_absolute_time(convo_timestamp, seconds_offset):
    parsed = parse(str(convo_timestamp), fuzzy=True)
    new_time = parsed + timedelta(seconds=float(str(seconds_offset)))
    pad = lambda x: "%02d" % (x,)
    time = ":".join([pad(new_time.hour), pad(new_time.minute), pad(new_time.second)])
    return time

def replace_offsets_with_abs_times(convo_lists, convo_timestamp):
    for i in range(len(convo_lists)):
        convo_lists[i][1] = offset_to_absolute_time(convo_timestamp, float(convo_lists[i][1]))
    return convo_lists


# generate a convo html that looks similar to iphone SMS dialog
def create_email_html_from_tuples(convo_tuples, recording_url, convo_timestamp):
    channel_mapping = {"channel0": "from", "channel1": "to"}

    html = """
    <html>
    <head>
    <style>
    .convo-transcript {width:100%;height:100%;}
    .message-row {}
    .message-box {width:75%;}
    .message-from {float:left;}
    .message-to {float:right;}
    </style>
    </head>
    <body>
        <div class="convo-transcript">
    """

    for row in convo_tuples:
        speaker = channel_mapping[row[0]]
        offset = row[1]
        true_start = offset_to_absolute_time(convo_timestamp, offset[0])
        html += '<div class="message-row"><p class="message-box message-' + speaker + '">' + \
                true_start + ': ' + str(row[2][0][0]) + \
                '<a href=' + recording_url + '#t=' + str(offset[0]) + ',' + str(offset[1]) + '>play</a><br></p>'

    html += """
    </div>
    </body>
    </html>
    """
    return html

def generate_html(transcript):
    try:
        convo_lists = create_convo_rows_from_multi_channel_transcript(transcript)
        html = create_email_html_from_tuples(
            convo_lists, transcript["recording_url"], transcript["timestamp"])
        return html
    except:
        sys.stderr.write(traceback.format_exc())
        return "html error"


parser = argparse.ArgumentParser()
parser.add_argument("-json", type=str, required=True, help="recording url")


if __name__ == "__main__":
    args = parser.parse_args()
    transcript = json.loads(open(args.json).read())
    html = generate_html(transcript)
    print html