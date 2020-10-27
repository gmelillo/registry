import requests
from packaging import version
import yaml
import json

versions = {}
url = f'https://hub.docker.com/v2/repositories/kindest/node/tags'

for ch in "OoYyNn":
    if len(yaml.resolver.Resolver.yaml_implicit_resolvers[ch]) == 1:
        del yaml.resolver.Resolver.yaml_implicit_resolvers[ch]
    else:
        yaml.resolver.Resolver.yaml_implicit_resolvers[ch] = [x for x in
                yaml.resolver.Resolver.yaml_implicit_resolvers[ch] if x[0] != 'tag:yaml.org,2002:bool']

while url is not None:
    print(url)
    response = requests.get(url)
    url = json.loads(response.text.encode('utf-8'))['next']
    for r in json.loads(response.text.encode('utf-8'))['results']:
        minor = '.'.join(r['name'][1:].split('.')[:2])
        if (minor not in versions or version.parse(versions[minor]) < version.parse(r['name'])) and version.parse(r['name']) >= version.parse('1.12'):
            versions[minor] = r['name']


for v in sorted(versions.values(), reverse=True):
    print(v)

with open('.github/workflows/ci.yaml', 'r') as f:
    y = yaml.safe_load(f.read())

y['jobs']['kubeval-chart']['strategy']['matrix']['k8s'] = sorted(versions.values(), reverse=True)
y['jobs']['install-chart']['strategy']['matrix']['k8s'] = sorted(versions.values(), reverse=True)

with open('.github/workflows/ci.yaml', 'w+') as f:
    f.write(yaml.safe_dump(y, default_flow_style=False, sort_keys=False))