import sqlite3


db = sqlite3.connect("eduu.db")
dbc = db.cursor()


dbc.execute(
    """CREATE TABLE IF NOT EXISTS groups (chat_id INTEGER PRIMARY KEY,
                                          welcome,
                                          welcome_enabled INTEGER,
                                          rules,
                                          goodbye,
                                          goodbye_enabled INTEGER,
                                          warns_limit INTEGER,
                                          chat_lang,
                                          cached_admins,
                                          antichannelpin,
                                          delservicemsgs)"""
)

dbc.execute(
    """CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY,
                                         chat_lang)"""
)

dbc.execute(
    """CREATE TABLE IF NOT EXISTS filters (chat_id INTEGER ,
                                           filter_name,
                                           raw_data,
                                           file_id,
                                           filter_type)"""
)

dbc.execute("""CREATE TABLE IF NOT EXISTS channels (chat_id INTEGER PRIMARY KEY)""")

dbc.execute(
    """CREATE TABLE IF NOT EXISTS was_restarted_at (chat_id INTEGER,
                                                    message_id INTEGER)"""
)


db.commit()
