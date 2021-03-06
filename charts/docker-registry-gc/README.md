# docker-registry-gc

![Version: 0.1.3](https://img.shields.io/badge/Version-0.1.3-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 0.1.4](https://img.shields.io/badge/AppVersion-0.1.4-informational?style=flat-square)

A Helm chart that deploy docker registry garbage collector cronjob

**Homepage:** <https://github.com/gmelillo/registry>

## Maintainers

| Name | Email | Url |
| ---- | ------ | --- |
| gabriel | gabriel@melillo.me |  |

## Source Code

* <https://github.com/gmelillo/registry>

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` |  |
| cronjob.annotations | object | `{}` |  |
| cronjob.concurrencyPolicy | string | `"Forbid"` |  |
| cronjob.failedJobsHistoryLimit | int | `1` |  |
| cronjob.labels | object | `{}` |  |
| cronjob.restartPolicy | string | `"OnFailure"` |  |
| cronjob.schedule | string | `"0 4 * * *"` |  |
| cronjob.successfulJobsHistoryLimit | int | `3` |  |
| env | object | `{}` |  |
| envFrom | list | `[]` |  |
| fullnameOverride | string | `""` |  |
| image.pullPolicy | string | `"Always"` |  |
| image.repository | string | `"gmelillo/registry"` |  |
| image.tag | string | `""` |  |
| imagePullSecrets | object | `{}` |  |
| nameOverride | string | `""` |  |
| nodeSelector | object | `{}` |  |
| pod.labels | object | `{}` |  |
| podSecurityContext | object | `{}` |  |
| registry.configMap | string | `"registry-config"` |  |
| resources | object | `{}` |  |
| secrets | object | `{}` |  |
| securityContext | object | `{}` |  |
| serviceAccount.annotations | object | `{}` |  |
| serviceAccount.create | bool | `true` |  |
| serviceAccount.name | string | `""` |  |
| tolerations | list | `[]` |  |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.4.0](https://github.com/norwoodj/helm-docs/releases/v1.4.0)
