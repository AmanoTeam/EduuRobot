import sqlite3


db = sqlite3.connect("eduu.db")
dbc = db.cursor()


dbc.execute("""CREATE TABLE IF NOT EXISTS groups (chat_id INTEGER,
                                                  welcome,
                                                  welcome_enabled INTEGER,
                                                  rules,
                                                  goodbye,
                                                  goodbye_enabled INTEGER,
                                                  warns_limit INTEGER,
                                                  chat_lang,
                                                  cached_admins)""")

dbc.execute("""CREATE TABLE IF NOT EXISTS users (user_id INTEGER,
                                                 chat_lang)""")

dbc.execute("""CREATE TABLE IF NOT EXISTS channels (chat_id INTEGER)""")

dbc.execute("""CREATE TABLE IF NOT EXISTS was_restarted_at (chat_id INTEGER,
                                                            message_id INTEGER)""")


db.commit()
