import os
import json
from src.utils import utils
from glob import glob
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from src import transcribe_url_async_gs
from src import html_from_transcript
from dateutil.parser import parse


email_file = utils.get_project_root() + "/credentials/email_account.json"
email_account = json.loads(open(email_file).read())


def pop_oldest(dir, delete=False):
    # get the oldest raw json (FIFO)
    f = sorted(glob(dir + "/*.txt"), reverse=False)[0]
    fname = os.path.basename(f)
    j = json.loads(open(f).read())
    if delete:
        os.remove(f)
    return fname, j

def send_user_email(html, subj, dest):
    # send just html to user
    fromaddr = email_account["address"]
    msg = MIMEMultipart()
    msg['From'] = email_account["account_name"]
    msg['To'] = dest
    msg['Subject'] = subj
    msg.attach(MIMEText(html, 'html'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, email_account["password"])
    text = msg.as_string()
    server.sendmail(fromaddr, dest, text)
    server.quit()

def send_server_email(html, body, subj):
    # send html and all metadata to server
    fromaddr = email_account["address"]
    dest = email_account["address"]
    msg = MIMEMultipart()
    msg['From'] = email_account["account_name"]
    msg['To'] = dest
    msg['Subject'] = subj
    msg.attach(MIMEText(html, 'html'))
    # put the body text in a div so it wont get jumbled with real html
    msg.attach(MIMEText(
        '<html><body><div style="display:inline-block">%s</div></body></html>' % body, 'html'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, email_account["password"])
    text = msg.as_string()
    server.sendmail(fromaddr, dest, text)
    server.quit()





if __name__ == "__main__":

    # the pull_dir acts as a queue for recordings to analyze.
    # analyzed data goes in the put_dir.

    pull_dir = utils.get_project_root() + "/data/raw/"
    put_dir = utils.get_project_root() + "/data/transcribed/"

    # load users file
    users = json.load(open(utils.get_project_root() + "/src/users.json"))

    # if files exist in pull dir
    if glob(pull_dir + "/*.txt"):

        # load a single recording json
        fname, j = pop_oldest(pull_dir, delete=True)
        recording_url = j["recording_url"]
        to_number = j["to"]
        from_number = j["from"]
        user_email = users[from_number]["email"]

        parsed_time = parsed = parse(j["timestamp"], fuzzy=True).strftime("%m/%d/%y %H:%M")

        # transcribe
        transcript = transcribe_url_async_gs.transcribe_audio_url(recording_url)

        # add transcript to json, save, and email
        j["transcript"] = transcript

        html = html_from_transcript.generate_html(j)
        send_user_email(
            html=html,
            subj="Your call with %s at %s" % (str(to_number), str(parsed_time)),
            dest=user_email)
        send_server_email(
            html=html,
            body=json.dumps(j, ensure_ascii=False),
            subj="%s called %s at %s" % (str(from_number), str(to_number), str(parsed_time)))
        # save data to put_dir
        with open(put_dir + fname, "w") as f:
            f.write(json.dumps(j, ensure_ascii=False))

