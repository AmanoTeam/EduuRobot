import httpx

from dbh import dbc, db


group_types = ("group", "supergroup")

http = httpx.AsyncClient(http2=True)


def add_chat(chat_id, chat_type):
    if chat_type == "private":
        dbc.execute("INSERT INTO users (user_id) values (?)", (chat_id,))
        db.commit()
    elif chat_type in group_types: # groups and supergroups share the same table
        dbc.execute("INSERT INTO groups (chat_id,welcome_enabled) values (?,?)", (chat_id, True))
        db.commit()
    elif chat_type == "channel":
        dbc.execute("INSERT INTO channels (chat_id) values (?)", (chat_id,))
        db.commit()
    else:
        raise TypeError("Unknown chat type '%s'." % chat_type)
    return True


def chat_exists(chat_id, chat_type):
    if chat_type == "private":
        dbc.execute("SELECT user_id FROM users where user_id = ?", (chat_id,))
        return bool(dbc.fetchone())
    if chat_type in group_types: # groups and supergroups share the same table
        dbc.execute("SELECT chat_id FROM groups where chat_id = ?", (chat_id,))
        return bool(dbc.fetchone())
    if chat_type == "channel":
        dbc.execute("SELECT chat_id FROM channels where chat_id = ?", (chat_id,))
        return bool(dbc.fetchone())
    raise TypeError("Unknown chat type '%s'." % chat_type)
