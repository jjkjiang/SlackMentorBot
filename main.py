import os

from slackclient import SlackClient

from google.cloud import firestore
from google.cloud.firestore_v1 import ArrayRemove, ArrayUnion
from google.api_core.exceptions import NotFound


# -----------------------------------------
# Individual bot actions
# -----------------------------------------
def add_keywords(mentor, keywords, db, sc):
    """Adds mentor references to firestore, if first one then creates a new document
    :param mentor: User ID of person who messaged bot
    :param keywords: Keywords user wants to add in string array
    :param db: Firestore client
    :param sc: Slack client
    """
    for keyword in keywords:
        entry = db.document('keyword', keyword)

        try:
            entry.update({'mentors': ArrayUnion([mentor])})
        except NotFound as e:
            entry.set({'mentors': [mentor]})

    reply_text = "I've added keywords " + str(keywords) + " to you!"

    sc.api_call(
        "chat.postMessage",
        as_user=True,
        channel=mentor,
        text=reply_text
    )


def remove_keywords(mentor, keywords, db, sc):
    """Removes mentor reference from firestore
    :param mentor: User ID of person who messaged bot
    :param keywords: Keywords user wants to remove in string array
    :param db: Firestore client
    :param sc: Slack client
    """
    for keyword in keywords:
        entry = db.document('keyword', keyword)

        try:
            entry.update({'mentors': ArrayRemove([mentor])})
        except NotFound as e:
            continue

    reply_text = "I've removed keywords " + str(keywords) + " to you!"

    sc.api_call(
        "chat.postMessage",
        as_user=True,
        channel=mentor,
        text=reply_text
    )


def print_help(mentor, sc):
    """Prints help text defined within this function to messaging user
    :param mentor: User ID of person who messaged bot
    :param sc: Slack client
    """
    help_text = "Welcome to MentorWatch." \
                "\n" \
                "I'm a service that lets you subscribe to keywords posted in the mentoring channel " \
                "and be notified if someone posts something that may apply to your areas of expertise or " \
                "interest. You can let me know what to look out for through private messages with me, " \
                "and also remove words as well." \
                "\n" \
                "To add words, say\n" \
                "\"add x1 x2 x3 ...\"\n" \
                "Where x1, x2, and x3 are all space delimited keywords you would like me to watch out for." \
                "\n" \
                "To remove words, say\n" \
                "\"remove x1 x2 x3 ...\"\n" \
                "Where x1, x2, and x3 are all space delimited keywords you no longer want to hear from." \
                "\n" \
                "For all of these, you can have as many keywords you like, but for your own sanity it's " \
                "recommended to exclude words like \"the\" to not get yourself spammed." \
                "\n" \
                "If you have any questions, dm jjkjiang on slack or email jjian014@ucr.edu"

    sc.api_call(
        "chat.postMessage",
        as_user=True,
        channel=mentor,
        text=help_text
    )


def start_pings(text, permalink, db, sc):
    """Checks a message for keywords and pings all subscribed mentors only ONCE per message
    :param text: String list with message components
    :param permalink: Link to original message
    :param db: Firestore client
    :param sc: Slack client
    """
    informed_users = set()

    for word in text:
        result = db.document('keyword', word).get()

        if result.exists:
            mentors = result.to_dict()['mentors']

            for mentor in mentors:
                if mentor in informed_users:
                    continue

                sc.api_call(
                    "chat.postMessage",
                    as_user=True,
                    channel=mentor,
                    text="This user might need your help: " + permalink,
                )

                informed_users.add(mentor)


# -----------------------------------------
# Main / cloud function handler
# -----------------------------------------
def receive_event(request):
    """Receives HTTP event subscriptions from Slack
    :param request: Flask request object
    :return:
    """

    db = firestore.Client()
    sc = SlackClient(os.environ["SLACK_API_TOKEN"])

    request_json = request.get_json()

    try:
        text = request_json['event']['text'].split()
    except KeyError e: # No text
        return

    text = clean_text(text)

    user = request_json['event']['user']

    if 'challenge' in request_json:
        return request_json['challenge']
    elif request_json['event']['channel_type'] == 'im':  # means likely mentor communication
        command = text[0]
        keywords = text[1:]

        if command == 'add':
            add_keywords(user, keywords, db, sc)
        elif command == 'remove':
            remove_keywords(user, keywords, db, sc)
        elif command == 'help':
            print_help(user, sc)

    elif request_json['event']['channel_type'] == 'channel': # means
        result = sc.api_call(
            "chat.getPermalink",
            channel=request_json['event']['channel'],
            message_ts=request_json['event']['ts'],
        )

        start_pings(text, result['permalink'], db, sc)

    return ""


# -----------------------------------------
# Helper functions
# -----------------------------------------

def clean_text(text):
    """Processes an array of strings to strip punctuation and capitalization
    :param text: String array
    :return: Cleaned string array with no punctuation and capitalization
    """
    result_text = []

    for word in text:
        # lowercase
        word = word.lower()
        # strip punctuation
        word = word.replace('.', '')\
            .replace('!', '')\
            .replace('?', '')\
            .replace('\'', '')\
            .replace('\"', '')

        result_text.append(word)

    return result_text
