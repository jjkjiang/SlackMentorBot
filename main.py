from google.cloud import firestore
from google.cloud.firestore_v1 import ArrayRemove, ArrayUnion
from google.api_core.exceptions import NotFound
import os
from slackclient import SlackClient


# -----------------------------------------
# Individual bot actions
# -----------------------------------------
def add_keywords(mentor, keywords, db):
    db.collection('keyword')

    for keyword in keywords:
        entry = db.document('keyword', keyword)

        try:
            entry.update({'mentors': ArrayUnion([mentor])})
        except NotFound as e:
            entry.set({'mentors': [mentor]})


def remove_keywords(mentor, keywords, db):
    db.collection('keyword')

    for keyword in keywords:
        entry = db.document('keyword', keyword)

        try:
            entry.update({'mentors': ArrayRemove([mentor])})
        except NotFound as e:
            continue


def print_help():
    return True


def start_pings(text, db):
    return True


# -----------------------------------------
# Main / cloud function handler
# -----------------------------------------
def receive_event(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """

    db = firestore.Client()
    sc = SlackClient(os.environ["SLACK_API_TOKEN"])

    request_json = request.get_json()

    text = request_json['event']['text'].split()
    text = [word.lower() for word in text]

    user = request_json['event']['user']

    if 'challenge' in request_json:
        return request_json['challenge']
    elif request_json['event']['channel_type'] == 'im':  # means likely mentor communication
        keywords = text[1:]

        if text[0].lower() == 'add':
            add_keywords(user, keywords, db)
        elif text[0].lower() == 'remove':
            remove_keywords(user, keywords, db)
        elif text[0].lower() == 'help':
            print_help()


    elif request_json['event']['channel_type'] == 'channel': # means
        keywords = text
        #filler

    return "ok"
# -----------------------------------------
# Helper functions
# -----------------------------------------


def grab_first_in_generator(gen):
    for i in gen:
        return i
