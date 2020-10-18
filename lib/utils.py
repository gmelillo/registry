import threading
import logging
import os
import signal
import subprocess
import shlex

class Command(object):
    def __init__(self, cmd, **kwargs):
        self.cmd = cmd
        self.process = None
        self.log = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

        self.timeout = kwargs.get('timeout', None)
        self.graceful_period = kwargs.get('graceful_period', 30)

    def run(self):
        def target():
            try:
                self.process = subprocess.Popen(shlex.split(self.cmd), shell=False, env=os.environ.copy(), 
                                                preexec_fn=os.setsid, stdout=subprocess.PIPE,
                                                stderr=subprocess.STDOUT)
            except Exception as e:
                self.log.error(f'unable to execute the command: {e.__str__()}')
                return
            while True:
                output = self.process.stdout.readline()
                if output:
                    self.log.info(output.strip())
                if self.process.poll() is not None:
                    break
            return self.process.poll()
        
        self.log.debug(f'Executing command {shlex.split(self.cmd)[0]} with {self.timeout}s of timeout and {self.graceful_period}s of grace period')

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(self.timeout)
        if thread.is_alive():
            os.killpg(self.process.pid, signal.SIGTERM)
            thread.join(self.graceful_period)
            if thread.is_alive():
                os.killpg(self.process.pid, signal.SIGKILL)
                thread.join()
        
        self.log.debug(f'Ececution of command {shlex.split(self.cmd)[0]} terminated')