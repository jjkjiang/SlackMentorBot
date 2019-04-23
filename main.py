from google.cloud import firestore
from google.cloud.firestore_v1beta1 import ArrayRemove, ArrayUnion


# -----------------------------------------
# Individual bot actions
# -----------------------------------------
def add_keywords(mentor, keywords, db):
    db.collection('keyword')

    for keyword in keywords:
        entry = db.document('keyword', keyword)

        snapshot = grabFirstInGenerator(entry.get())
        if snapshot.exists():
            entry.update({'mentors': ArrayUnion([mentor])})
        else:
            entry.set({
                'mentors': mentor,
            })


def remove_keywords(mentor, keywords, db):
    return True


def reply(text, db):
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

    request_json = request.get_json()

    text = request_json['event']['text'].split()
    user = request_json['event']['user']

    if 'challenge' in request_json:
        return request_json['challenge']
    elif request_json['event']['channel_type'] == 'im':  # means likely mentor communication
        keywords = text[1:]

        if text[0].lower() == 'add':
            add_keywords(user, keywords, db)

    elif request_json['event']['channel_type'] == 'channel': # means
        keywords = text
        #filler

    return "ok"
# -----------------------------------------
# Helper functions
# -----------------------------------------

def grabFirstInGenerator(gen):
    for i in gen:
        return i

