
# ============================================================================ #
#  While in the task description there was nothing about command line          #
#  interface I've made this script simple and stupid: just one iteration       #
#  in a run.                                                                   #
#                                                                              #
#  Also I left (after debug) some output about steps' results to the terminal. #
#  just delete it if your don't need.                                          #
# ============================================================================ #

from locale import setlocale, LC_ALL
from tinkoff_voicekit_client import ClientSTT
from auxiliary import *
from datetime import datetime as dt
from uuid import uuid4
from psycopg2 import connect as connectDB
from os import remove

setlocale(LC_ALL, 'ru_RU.UTF-8')


class ScriptFailure(Exception):
    # this overrides initialization method to write down log of errors
    def __init__(self, message, errors):
        with open("errors.log", 'w', encoding='utf-8', newline='\r\n') as f_out:
            f_out.writelines(errors)
        super().__init__(message)


# dancing with interface of STT service
client = ClientSTT(API_KEY, SECRET_KEY)
audio_config = {
    "encoding": "LINEAR16",
    "sample_rate_hertz": 8000,
    "num_channels": 1
}
errors = []

# =================================== STEP 1 ===================================
# input string format:
# filepath: str, phone number: str, recognition phase: str, database flag: bool

# creating unique number for this operation
oper_id = uuid4().hex
# single-line input
args = input().split()
# multi-line input
# args = []
# for _ in range(4):
#     args.append(input())
# check for correct input
if len(args) == 4:
    if args[0][-3:] != "wav":
        errors.append(f"{oper_id}. Wrong input: expected WAV file\n")
    if not args[1].isdigit():
        errors.append(f"{oper_id}. Wrong input: expected only digits in phone number\n")
    # 11 digits if it will process only russian phone numbers
    #  change for other standards
    if len(args[1]) != 11:
        errors.append(f"{oper_id}. Wrong input: expected 11 digits phone number\n")
    if args[2].lower() in ['1', 'i', 'a', 'first', 'первый']:
        args[2] = 1
    elif args[2].lower() in ['2', 'ii', 'b', 'second', 'второй']:
        args[2] = 2
    # for next phases in future
    # elif args[2].lower() in ['3', 'iii', 'c', 'third', 'третий']:
    #     args[2] = 3
    else:
        errors.append(f"{oper_id}. Wrong input: expected existing recognition phase number\n")
    if args[3] in ['0', 'False', 'no', 'нет']:
        args[3] = False
    elif args[3] in ['1', 'True', 'yes', 'да']:
        args[3] = True
    else:
        errors.append(f"{oper_id}. Wrong input: expected boolean-like database flag\n")
else:
    errors.append(f"{oper_id}. Wrong input: expected 4 arguments\n")

# it had been decided to process and log all input errors before interrupt the script
if errors:
    raise ScriptFailure("Step 1 failure. Check errors.log", errors)
print("Step 1 success. Input accepted")

# =================================== STEP 2 ===================================
# as we saw from the examples the response list is already sorted from max (absolute) confidence,
#  so the first entry in list is the one we need
try:
    response = client.recognize(args[0], audio_config)
    text = response[0]['alternatives'][0]['transcript']
    # check if we have any text to process
    if not text:
        errors.append(f"{oper_id}. No speech has been recognized")
        raise ScriptFailure("Step 2 failure. Check errors.log", errors)
    else:
        print("Step 2 success. STT service responded")
except Exception as e:
    errors.append(f"{oper_id}. {e.args[0]}\n")
    raise ScriptFailure("Step 2 failure. Check errors.log", errors)

# =================================== STEP 3 ===================================
try:
    # phase 1
    if args[2] == 1:
        action_result = check_voicemail(text, True)
        recog_result = check_voicemail(text)
    # phase 2
    elif args[2] == 2:
        action_result = process_answer(text, True)
        recog_result = process_answer(text)
    # for next phases in future
    # elif args[2] == 3:
    #     pass
    print("Step 3 success. The recognition result was processed")
except Exception as e:
    errors.append(f"{oper_id}. {e.args[0]}\n")
    raise ScriptFailure("Step 3 failure. Check errors.log", errors)

# =================================== STEP 4 ===================================
try:
    # result dictionary for this iteration
    result = {
        'datetime': dt.now().strftime("%Y-%m-%d %H:%M:%S"),
        'id': oper_id,
        'action_result': action_result,
        'phone_number': args[1],
        'speech_duration': float(response[0]['end_time'][:-1]) -
                           float(response[0]['start_time'][:-1]),
        'recognition_result': recog_result
    }
    # appending this result to the results.log file
    with open("results.log", 'a', encoding='utf-8', newline='\r\n') as f_out:
        f_out.writelines([str(i)+'\n' for i in result.values()])
        f_out.write('\n')
    print("Step 4 success. Check results.log")
except Exception as e:
    errors.append(f"{oper_id}. {e.args[0]}\n")
    raise ScriptFailure("Step 4 failure. Check errors.log", errors)

# =================================== STEP 5 ===================================
# database part
if args[3]:
    try:
        connection = connectDB(
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        connection.autocommit = True
        cursor = connection.cursor()
        # if you still don't have any table in your database
        cursor.execute(DB_CREATE_RESULTS_TABLE)
        cursor.execute(DB_INSERT_QUERY.format(','.join([*result.keys()]),
                                              ','.join(['%s'] * len(result))),
                       [*result.values()])
        print(f"Step 5 success. Database {DB_NAME} was updated")
    except Exception as e:
        errors.append(f"{oper_id}. {e.args[0]}\n")
        raise ScriptFailure("Step 5 failure. Check errors.log", errors)
else:
    print("Step 5 skipped.")

# =================================== STEP 6 ===================================
# removes file: by the way, why do you need this?
try:
    remove(args[0])
    print(f"Step 6 success. File \'{args[0]}\' was removed")
except Exception as e:
    errors.append(f"{oper_id}. {e.args[0]}\n")
    raise ScriptFailure("Step 6 failure. Check errors.log", errors)

# =================================== STEP 7 ===================================
# there should be no errors at this moment, but who knows...
if errors:
    raise ScriptFailure("Check errors.log", errors)
else:
    print("Step 7 success. No errors occurred")
