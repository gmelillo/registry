import json
from kubernetes import client, config
from kubernetes.client.api import apps_v1_api
from kubernetes.client import api_client
from time import time, sleep
from logging import getLogger

from kubernetes.client.rest import ApiException

class KubeException(Exception):
    pass

class KubeObj(object):
    def __init__(self, config_file=None) -> None:
        self.log = getLogger(f'{__name__}.{self.__class__.__name__}')
        if config_file is None:
            try:
                config.load_kube_config()
            except:
                config.load_incluster_config()
            self.api = client.AppsV1Api()
        else:
            self.api = apps_v1_api.AppsV1Api(api_client.ApiClient(configuration=config_file))

class Deployment(KubeObj):
    def __init__(self, name: str, namespace: str, config_file=None) -> None:
        self.namespace = namespace
        self.deployment = name
        super().__init__(config_file=config_file)
        d = self.data
        if d is None:
            raise KubeException(f'unable to find deployment {self.deployment} in namespace {self.namespace}')
 
    def get_deployment(self):
        return self.api.read_namespaced_deployment(self.deployment, self.namespace)

    def patch_deployment(self, body):
        return self.api.patch_namespaced_deployment(self.deployment, self.namespace, body)

    def get_deployment_status(self):
        return self.api.read_namespaced_deployment_status(self.deployment, self.namespace)

    @property
    def data(self):
        try:
            return self.get_deployment()
        except ApiException as e:
            self.log.critical(f'unable to find deployment {self.deployment} in namespace {self.namespace}; {e.reason}', exc_info=True, stack_info=False)
            raise KubeException(f'{e.status}: {e.reason}')
        except Exception as e:
            self.log.critical(f'unable to find deployment {self.deployment} in namespace {self.namespace}', exc_info=True, stack_info=True)
            raise KubeException(e.__str__())


    def wait_for_complete(self, timeout=600):
        start = time()
        while time() - start < timeout:
            response = self.get_deployment_status()
            s = response.status
            if (s.updated_replicas == response.spec.replicas and
                    s.replicas == response.spec.replicas and
                    s.available_replicas == response.spec.replicas and
                    s.observed_generation >= response.metadata.generation):
                return True
            else:
                self.log.info(f'[updated_replicas:{s.updated_replicas},replicas:{s.replicas}'
                    f',available_replicas:{s.available_replicas},observed_generation:{s.observed_generation}] waiting...')
            sleep(2)

        raise RuntimeError(f'Waiting timeout for deployment {self.deployment}')
    
    def patch(self, body):
        self.patch_deployment(body)
        self.wait_for_complete()

class Registry(Deployment):
    def __init__(self, name, namespace, config_file=None):
        super().__init__(name, namespace, config_file=config_file)

    @property
    def is_readonly(self) -> bool:
        deployment = self.data
        for container in deployment.spec.template.spec.containers:
            if container.env is None:
                return False
            for env in container.env:
                if env.name == "REGISTRY_STORAGE_MAINTENANCE_READONLY":
                    try:
                        return json.loads(env.value)['enabled']
                    except Exception as e:
                        self.log.error("Unable to unmarshal the status", e.__str__())
        return False

    def set_environment(self, name, value):
        deployment = self.data
        for env in deployment.spec.template.spec.containers[0].env:
            if env.name == name:
                env.value = value
                break
        else:
            deployment.spec.template.spec.containers[0].env.append(client.V1EnvVar(name, value))
        self.patch(deployment)

    def readOnly(self, status: bool):
        self.set_environment('REGISTRY_STORAGE_MAINTENANCE_READONLY', json.dumps({'enabled': status}))