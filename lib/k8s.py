import json
from kubernetes import client, config
from time import time, sleep
from logging import getLogger

from kubernetes.client.rest import ApiException

class KubeException(Exception):
    pass

class KubeObj(object):
    def __init__(self) -> None:
        self.log = getLogger(f'{__name__}.{self.__class__.__name__}')
        try:
            config.load_kube_config()
        except:
            config.load_incluster_config()
        self.api = client.AppsV1Api()

class Deployment(KubeObj):
    def __init__(self, name: str, namespace: str) -> None:
        self.namespace = namespace
        self.deployment = name
        super().__init__()
        d = self.data
        if d is None:
            raise KubeException(f'unable to find deployment {self.deployment} in namespace {self.namespace}')
 
    @property
    def data(self):
        try:
            return self.api.read_namespaced_deployment(self.deployment, self.namespace)
        except ApiException as e:
            self.log.critical(f'unable to find deployment {self.deployment} in namespace {self.namespace}; {e.reason}', exc_info=True, stack_info=False)
            raise KubeException(f'{e.status}: {e.reason}')
        except Exception as e:
            self.log.critical(f'unable to find deployment {self.deployment} in namespace {self.namespace}', exc_info=True, stack_info=True)
            raise KubeException(f'{e.status}: {e.reason}')


    def wait_for_complete(self, timeout=600):
        start = time()
        while time() - start < timeout:
            sleep(2)
            response = self.api.read_namespaced_deployment_status(self.deployment, self.namespace)
            s = response.status
            if (s.updated_replicas == response.spec.replicas and
                    s.replicas == response.spec.replicas and
                    s.available_replicas == response.spec.replicas and
                    s.observed_generation >= response.metadata.generation):
                return True
            else:
                self.log.info(f'[updated_replicas:{s.updated_replicas},replicas:{s.replicas}'
                    f',available_replicas:{s.available_replicas},observed_generation:{s.observed_generation}] waiting...')

        raise RuntimeError(f'Waiting timeout for deployment {self.deployment}')
    
    def patch(self, body):
        self.api.patch_namespaced_deployment(self.deployment, self.namespace, body)
        self.wait_for_complete()

class Registry(Deployment):
    def __init__(self, name, namespace):
        super().__init__(name, namespace)

    @property
    def is_readonly(self) -> bool:
        deployment = self.data
        for container in deployment.spec.template.spec.containers:
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