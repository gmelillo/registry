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
    parser = argparse.ArgumentParser(description='Preparation for docker registry garbage collector.')
    parser.add_argument('-n', '--namespace', default='docker', help='namespace having docker registry installed')
    parser.add_argument('-d', '--deployment', default='registry', help='docker registry eployment name')
    parser.add_argument('-t', '--timeout', default=int(12*60*60), type=int, help='timeout for running the garbage collector')

    args = parser.parse_args()

    return args

def main():
    jsonlogs.setup_logging()
    args = parse_args()

    try:
        registry = Registry(args.deployment, args.namespace)
        
        if not registry.is_readonly:
            registry.readOnly(True)
        Command('/bin/registry garbage-collect --delete-untagged=true /etc/docker/registry/config.yml').run(args.timeout)
        if registry.is_readonly:
            registry.readOnly(False)
    except Exception as e:
        LOG.error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()