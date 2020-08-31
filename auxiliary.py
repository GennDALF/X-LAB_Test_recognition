
from config import *


def check_voicemail(text, string_return=False):
    if "автоответчик" in text or \
       all(word in text for word in ["оставьте", "сообщение"]):
        if not string_return:
            return 0
        else:
            return "voicemail"
    else:
        if not string_return:
            return 1
        else:
            return "human"


def process_answer(text, string_return=False):
    if any(word in text for word in NEGATIVE_WORDS):
        if not string_return:
            return 0
        else:
            return "negative"
    elif any(word in text.split() for word in POSITIVE_WORDS) and \
            not any(word in text for word in NEGATIVE_WORDS):
        if not string_return:
            return 0
        else:
            return "positive"
    else:
        # we got here if we couldn't recognize any clear reaction in the response
        #  which means that:
        #   (a) STT service made a mistake during recognition
        #   (b) our words' base needs to be updated accordingly
        #   (c) our client is far from 3-sigma interval and we can forget him
        #  anyway this case should be processed by a person
        if not string_return:
            return 0
        else:
            return "unclear"
