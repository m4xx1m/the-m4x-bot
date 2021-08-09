import time
import datetime

start_time = time.time()


def get_uptime():
    return str(datetime.timedelta(seconds=round(time.time() - start_time)))
