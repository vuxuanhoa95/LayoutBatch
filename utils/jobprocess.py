import logging
import subprocess
import threading
import os
import sys
import time


TEMP = r'C:\Dev\temp'
date_time = time.strftime("%Y%m%d%H%M%S")
LOG_FILE = os.path.join(TEMP, f'test.{date_time}.log')
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, filename=LOG_FILE, format='%(asctime)s %(message)s')


def call(*args):

    def run_in_thread(arguments, on_exit, on_progress, on_log):

        proc = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                creationflags=subprocess.CREATE_NEW_CONSOLE)

        def check_io():
            i = 0
            while True:
                i += 1
                if i >= 100:
                    i = 1
                on_progress(i)  # progress callback
                output = proc.stdout.readline().decode()
                if output:
                    logger.log(logging.INFO, output)
                    on_log(output)  # log callback

                else:
                    break

        while proc.poll() is None:
            check_io()

        proc.wait()
        on_exit()  # exit callback

    thread = threading.Thread(target=run_in_thread, args=args)
    return thread
