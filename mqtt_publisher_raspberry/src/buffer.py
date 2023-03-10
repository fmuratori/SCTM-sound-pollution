from threading import Condition
from time import time
import logging
from datetime import datetime

BUFFER_SIZE = 60*24

# TODO: valutare l'utilizzo di numpy

class BoundedBuffer:
    buffer = []
    size = None
    update_event = None

    lock = Condition() # prevents race conditions

    def __init__(self, size, buffer_update_event):
        self.size = size if size is not None else BUFFER_SIZE
        self.update_event = buffer_update_event;

    def is_full(self):
        with self.lock:
            return len(self.buffer) >= self.size
    
    def is_empty(self):
        with self.lock:
            return len(self.buffer) == 0

    def put(self, value):
        # shift buffer to the left
        with self.lock:
            curr_time = datetime.utcnow().isoformat()
            if self.is_full():
                logging.info(f"[BUFFER] Buffer is full. Shifting values...")
                self.buffer = self.buffer[1:] + [(curr_time, value)]
            else:
                self.buffer.append((curr_time, value))
            self.update_event.set()
    
    def flush_all(self):
        with self.lock:
            logging.info(f"[BUFFER] Buffer flushed.")
            old_buffer = self.buffer.copy()
            self.buffer = []
            return old_buffer