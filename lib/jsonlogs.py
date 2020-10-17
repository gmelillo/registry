import logging
import sys
import json
from enum import Enum

class LogEnum(Enum):
    def __str__(self) -> str:
        return str(self.name)

class LogFormat(LogEnum):
    json = None
    pretty = 4

    @classmethod
    def favorite(cls):
        cls.json
class LogLevel(LogEnum):
    critical = logging.CRITICAL
    fatal = logging.FATAL
    error = logging.ERROR
    warning = logging.WARNING
    info = logging.INFO
    debug = logging.DEBUG
    notset = logging.NOTSET

    def __str__(self) -> str:
        return str(self.name)

    @classmethod
    def favorite(cls):
        cls.info

def setup_logging(format: LogFormat, log_level: LogLevel):
    class JSONLogFormatter(logging.Formatter):
        def __init__(self):
            pass
        def format(self, record):
            ret = {}
            ret.update(record.__dict__)
            ret['message'] = record.getMessage()
            for i in ('exc_info', 'exc_text', 'args', 'relativeCreated', 'name', 'thread',
                      'msecs', 'pathname', 'processName', 'levelno', 'msg', 'stack_info'):
                if i in ret:
                    del ret[i]
            ret['level'] = ret['levelname']
            del ret['levelname']
            ret['timestamp'] = int(ret['created'] * 1000)
            del ret['created']
            if record.exc_info:
                if not record.exc_text:
                    record.exc_text = self.formatException(record.exc_info)
            if record.exc_text:
                try:
                    ret['message'] += record.exc_text
                except UnicodeError:
                    # see python's logging formatter for an explanation of this
                    ret['message'] += record.exc_text.decode(sys.getfilesystemencoding(), 'replace')
            return json.dumps(ret, indent=format.value)

    rootLogger = logging.getLogger()
    hnd = logging.StreamHandler(sys.stdout)
    hnd.setFormatter(JSONLogFormatter())
    rootLogger.setLevel(log_level.value)
    hnd.setLevel(log_level.value)
    rootLogger.addHandler(hnd)
