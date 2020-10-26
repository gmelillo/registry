import requests
from packaging import version
from os import environ
import yaml

versions = {}
url = 'https://api.github.com/repos/kubernetes/kubernetes/releases'
headers = {"Authorization": f"token {environ.get('GITHUB_TOKEN')}"}

for ch in "OoYyNn":
    if len(yaml.resolver.Resolver.yaml_implicit_resolvers[ch]) == 1:
        del yaml.resolver.Resolver.yaml_implicit_resolvers[ch]
    else:
        yaml.resolver.Resolver.yaml_implicit_resolvers[ch] = [x for x in
                yaml.resolver.Resolver.yaml_implicit_resolvers[ch] if x[0] != 'tag:yaml.org,2002:bool']

while True:
    response = requests.get(url, headers=headers)
    print(url)
    try:
        url = [l.split(';')[0].replace('<', '').replace('>', '') for l in response.headers['link'].split(', ') if 'rel="next"' in l][0]
    except:
        url = None

    for r in response.json():
        if r.get('name', None) is not None:
            if '-alpha' not in r['name'] and '-rc' not in r['name']:
                minor = '.'.join(r['name'][1:].split('.')[:2])
                if (minor not in versions or version.parse(versions[minor]) < version.parse(r['name'])) and version.parse(r['name']) > version.parse('1.11'):
                    versions[minor] = r['name']
    
    if url is None:
        break


for v in sorted(versions.values(), reverse=True):
    print(v)

with open('.github/workflows/ci.yaml', 'r') as f:
    y = yaml.safe_load(f.read())

y['jobs']['kubeval-chart']['strategy']['matrix']['k8s'] = sorted(versions.values(), reverse=True)
y['jobs']['install-chart']['strategy']['matrix']['k8s'] = sorted(versions.values(), reverse=True)

with open('.github/workflows/ci.yaml', 'w+') as f:
    f.write(yaml.safe_dump(y, default_flow_style=False, sort_keys=False))