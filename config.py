
API_KEY = "key"
SECRET_KEY = "secret-key"

POSITIVE_WORDS = [
    "да",
    "конечно",
    "говорите",
    "слушаю",
    "удобно"
]
NEGATIVE_WORDS = [
    "нет",
    "неудобно",
    "не удобно",
    "не сейчас",
    "до свидания"
]

# you must fill in actual values to connect to an existing database
DB_NAME = "stt"
DB_USER = "admin"
DB_PASSWORD = "password"
DB_HOST = "127.0.0.1"
DB_PORT = "5432"
DB_TABLE = "results"

DB_CREATE_RESULTS_TABLE = (f"CREATE TABLE IF NOT EXISTS {DB_TABLE} (\n"
                           "  datetime TEXT NOT NULL,\n"
                           "  id TEXT PRIMARY KEY,\n"
                           "  action_result TEXT NOT NULL,\n"
                           "  phone_number TEXT NOT NULL,\n"
                           "  speech_duration NUMERIC NOT NULL,\n"
                           "  recognition_result INTEGER NOT NULL,\n"
                           "  project_id INTEGER REFERENCES project (id),\n"
                           "  server_id INTEGER REFERENCES  server (id));")
DB_INSERT_QUERY = (f"INSERT INTO {DB_TABLE} \n"
                   "   ({}) \n"
                   "VALUES ({})")
