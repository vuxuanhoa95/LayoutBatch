import logging
import subprocess
import threading
import os

TEMP = r'D:\temp'
LOG_FILE = os.path.join(TEMP, 'test.log')
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, filename=LOG_FILE, format='%(message)s')


def call(*args):
    """
    Runs the given args in a subprocess.Popen, and then calls the function
    on_exit when the subprocess completes.
    on_exit is a callable object, and popen_args is a list/tuple of args that
    would give to subprocess.Popen.
    """

    def run_in_thread(arguments, on_exit, on_progress, on_log):

        proc = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
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
                    # logger.log(logging.INFO, output)
                    on_log(output[:63])  # log callback
                else:
                    break

        while proc.poll() is None:
            check_io()

        proc.wait()
        on_exit()  # exit callback

    thread = threading.Thread(target=run_in_thread, args=args)
    # thread.start()
    # returns immediately after the thread starts
    return thread
