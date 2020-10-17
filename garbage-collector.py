#!/usr/bin/env python3

from enum import Enum
import os
import logging
import sys
import argparse

sys.path.insert(0, os.path.join(os.path.realpath(os.path.split(sys.modules['__main__'].__file__)[0]), 'lib'))

import jsonlogs
from k8s import Registry
from utils import Command

LOG = logging.getLogger()

def parse_args():
    parser = argparse.ArgumentParser(description='Preparation for docker registry garbage collector.', 
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-n', '--namespace', default=os.environ.get('GARBAGE_COLLECTOR_NAMESPACE', 'docker'), 
                        help='namespace having docker registry installed')
    parser.add_argument('-d', '--deployment', default=os.environ.get('GARBAGE_COLLECTOR_DEPLOYMENT', 'registry'), 
                        help='docker registry eployment name')
    parser.add_argument('-t', '--timeout', default=int(os.environ.get('GARBAGE_COLLECTOR_TIMEOUT', '43200'), base=10), 
                        type=int, help='timeout for running the garbage collector')
    parser.add_argument('--log-format', type=lambda c: jsonlogs.LogFormat[c], choices=list(jsonlogs.LogFormat), 
                        default=os.environ.get('GARBAGE_COLLECTOR_LOG_FORMAT', 'pretty'), 
                        help='Format of the logs.')
    parser.add_argument('--log-level', type=lambda c: jsonlogs.LogLevel[c], choices=list(jsonlogs.LogLevel), 
                        default=os.environ.get('GARBAGE_COLLECTOR_LOG_LEVEL', 'info'), 
                        help='Format of the logs.')
    parser.add_argument('--graceful-period', default=int(os.environ.get('GARBAGE_COLLECTOR_GRACEFUL_PERIOD', '43200'), base=10),
                        type=int, help='second allowed for the registry to shutdown correctly before kill')

    args = parser.parse_args()

    return args

def main():
    args = parse_args()
    jsonlogs.setup_logging(args.log_format, args.log_level)

    try:
        registry = Registry(args.deployment, args.namespace)
        
        if not registry.is_readonly:
            registry.readOnly(True)
        Command('/bin/registry garbage-collect --delete-untagged=true /etc/docker/registry/config.yml', 
                timeout=args.timeout, graceful_period=args.graceful_period).run()
        if registry.is_readonly:
            registry.readOnly(False)
    except Exception as e:
        LOG.error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()