import unittest
from unittest import mock

from kubernetes.client import api_client

import lib.k8s as k8s
import os
import unittest
import urllib3
import json
from kubernetes.client.configuration import Configuration
from kubernetes.config import kube_config

DEFAULT_E2E_HOST = '127.0.0.1'

from dataclasses import dataclass, replace
@dataclass
class FakeKube(object):
    def __init__(self, file, ):
        with open(file, 'r') as f:
            self.data = f.read()
    def load(self):
        return api_client.ApiClient().deserialize(self, 'V1Deployment')

def get_e2e_configuration():
    config = Configuration()
    config.host = None
    if os.path.exists(
            os.path.expanduser(kube_config.KUBE_CONFIG_DEFAULT_LOCATION)):
        kube_config.load_kube_config(client_configuration=config)
    else:
        print('Unable to load config from %s' %
              kube_config.KUBE_CONFIG_DEFAULT_LOCATION)
        for url in ['https://%s:8443' % DEFAULT_E2E_HOST,
                    'http://%s:8080' % DEFAULT_E2E_HOST,
                    'http://%s:6443' % DEFAULT_E2E_HOST]:
            try:
                urllib3.PoolManager().request('GET', url)
                config.host = url
                config.verify_ssl = False
                urllib3.disable_warnings()
                break
            except urllib3.exceptions.HTTPError:
                pass
    if config.host is None:
        raise unittest.SkipTest('Unable to find a running Kubernetes instance')
    print('Running test against : %s' % config.host)
    config.assert_hostname = False
    return config

class TestMerger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = get_e2e_configuration()
    
    def test_kube_obj(self):
        k = k8s.KubeObj(self.config)
        self.assertIsNotNone(k.api.api_client.configuration.api_key, dict({'authorization': 'Basic a3ViZXJuZXRlczpzb21lLXBhc3N3b3Jk'}))

    def test_deployment_wait_for_complete(self):
        with mock.patch('lib.k8s.Deployment.get_deployment', return_value=FakeKube(os.getcwd() + '/test/mock/read_namespaced_deployment.json').load()):
            d = k8s.Deployment('registry', 'stocazzo', self.config)
        with mock.patch('lib.k8s.Deployment.get_deployment_status', return_value=FakeKube(os.getcwd() + '/test/mock/read_namespaced_deployment.json').load()):
            with self.assertRaises(RuntimeError):
                d.wait_for_complete(timeout=1)
        with mock.patch('lib.k8s.Deployment.get_deployment_status', return_value=FakeKube(os.getcwd() + '/test/mock/read_namespaced_deployment_ok.json').load()):
            self.assertTrue(d.wait_for_complete(timeout=30))

    def test_registry_is_readonly(self):
        with mock.patch('lib.k8s.Deployment.get_deployment', return_value=FakeKube(os.getcwd() + '/test/mock/read_namespaced_deployment.json').load()):
            d = k8s.Registry('registry', 'stocazzo', self.config)

        with mock.patch('lib.k8s.Deployment.get_deployment', return_value=FakeKube(os.getcwd() + '/test/mock/read_namespaced_deployment.json').load()):
            self.assertFalse(d.is_readonly)
        with mock.patch('lib.k8s.Deployment.get_deployment', return_value=FakeKube(os.getcwd() + '/test/mock/read_namespaced_deployment_registry_ro.json').load()):
            self.assertTrue(d.is_readonly)

    def test_registry_set_environment(self):
        pass

if __name__ == '__main__':
    unittest.main()
