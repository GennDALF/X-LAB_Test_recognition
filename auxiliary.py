
from config import *


def check_input(oper_id, args_list):
    errors = []
    if len(args_list) == 4:
        if args_list[0][-3:] != "wav":
            errors.append(f"{oper_id}. Wrong input: expected WAV file\n")
        if not args_list[1].isdigit():
            errors.append(f"{oper_id}. Wrong input: expected only digits in phone number\n")
        # 11 digits if it will process only russian phone numbers
        #  change for other standards
        if len(args_list[1]) != 11:
            errors.append(f"{oper_id}. Wrong input: expected 11 digits phone number\n")
        if args_list[2].lower() in ['1', 'i', 'a', 'first', 'первый']:
            args_list[2] = 1
        elif args_list[2].lower() in ['2', 'ii', 'b', 'second', 'второй']:
            args_list[2] = 2
        # for next phases in future
        # elif args[2].lower() in ['3', 'iii', 'c', 'third', 'третий']:
        #     args[2] = 3
        else:
            errors.append(f"{oper_id}. Wrong input: expected existing recognition phase number\n")
        if args_list[3] in ['0', 'False', 'no', 'нет']:
            args_list[3] = False
        elif args_list[3] in ['1', 'True', 'yes', 'да']:
            args_list[3] = True
        else:
            errors.append(f"{oper_id}. Wrong input: expected boolean-like database flag\n")
    else:
        errors.append(f"{oper_id}. Wrong input: expected 4 arguments\n")
    return errors


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
            return 1
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
            return -1
        else:
            return "unclear"
