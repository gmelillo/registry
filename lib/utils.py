import threading
import logging
import os
import signal
import subprocess

class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
        self.log = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

    def run(self, timeout):
        def target():
            try:
                self.process = subprocess.Popen(self.cmd, shell=False, preexec_fn=os.setsid, stdout=subprocess.PIPE)
            except Exception as e:
                self.log.error(f'unable to execute the garbage collector: {e.__str__()}')
                return
            while True:
                output = self.process.stdout.readline()
                if self.process.poll() is not None:
                    break
                if output:
                    self.log.info(output.strip())
            return self.process.poll()

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            os.killpg(self.process.pid, signal.SIGTERM)
            thread.join()