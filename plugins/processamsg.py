import time
import config
from db_handler import *
import threading

lock = threading.Lock()

def processamsg(msg):
    if msg.get('date'):
        if time.time() - msg['date'] > config.max_time:
            return True
        elif msg.get('chat'):
        	try:
        		lock.acquire(True)
        		add_chat(msg['chat']['type'], msg['chat']['id'])
        	finally:
        		lock.release()
