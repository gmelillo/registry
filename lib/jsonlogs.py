import logging
import sys
import json

def setup_logging():
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
            return json.dumps(ret)

    rootLogger = logging.getLogger()
    hnd = logging.StreamHandler(sys.stdout)
    hnd.setFormatter(JSONLogFormatter())
    rootLogger.setLevel(20)
    hnd.setLevel(20)
    rootLogger.addHandler(hnd)
