from kubernetes import client, config
from time import time, sleep
from json import dumps
import subprocess, threading, signal, os
from sys import exit

class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    def run(self, timeout):
        def target():
            self.process = subprocess.Popen(self.cmd, shell=True, preexec_fn=os.setsid)
            self.process.communicate()

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            os.killpg(self.process.pid, signal.SIGTERM)
            thread.join()

class Registry(object):
    def __init__(self, deployment, namespace):
        self.deployment = deployment
        self.namespace = namespace
        try:
            config.load_kube_config()
        except:
            config.load_incluster_config()
        self.api = client.AppsV1Api()

    def _get_deployment(self):
        return self.api.read_namespaced_deployment(self.deployment, self.namespace)

    def _wait_for_deployment_complete(self, timeout=600):
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
                print(f'[updated_replicas:{s.updated_replicas},replicas:{s.replicas}'
                    f',available_replicas:{s.available_replicas},observed_generation:{s.observed_generation}] waiting...')

        raise RuntimeError(f'Waiting timeout for deployment {self.deployment}')

    def _patch_deployment(self, body):
        self.api.patch_namespaced_deployment(self.deployment, self.namespace, body)
        self._wait_for_deployment_complete()

    def set_environment(self, name, value):
        deployment = self._get_deployment()
        for env in deployment.spec.template.spec.containers[0].env:
            if env.name == name:
                env.value = value
                break
        else:
            deployment.spec.template.spec.containers[0].env.append(client.V1EnvVar(name, value))
        self._patch_deployment(deployment)

    def readOnly(self, status: bool):
        self.set_environment('REGISTRY_STORAGE_MAINTENANCE_READONLY', dumps({'enabled': status}))
        
def main():
    try:
        registry = Registry('registry', 'docker')
        registry.readOnly(True)
        Command('/bin/registry garbage-collect --delete-untagged=true /etc/docker/registry/config.yml').run(int(12*60*60))
        registry.readOnly(False)
    except Exception as e:
        print(e)
        exit(1)


if __name__ == "__main__":
    main()