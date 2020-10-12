# registry

Wrapper of the registry intended to schedule garbage collector run on k8s cluster

## Service Account

The following service account is needed to run the container

```kubernetes
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: registry-garbage-collector
---
kind: Role
apiVersion: rbac.authorization.k8s.io/v1beta1
metadata:
  name: registry-garbage-collector
rules:
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get","list","patch","update","watch"]
- apiGroups: ["apps"]
  resources: ["deployments/status"]
  verbs: ["get","list","watch"]
---
apiVersion: rbac.authorization.k8s.io/v1beta1
kind: RoleBinding
metadata:
  name: registry-garbage-collector
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: registry-garbage-collector
subjects:
- kind: ServiceAccount
  name: registry-garbage-collector
```

## CronJob

Example of cronjob that use the container to run the garbage collector on a registry that is using S3 as backend

```kubernetes
---
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: docker-registry-garbage-collector
spec:
  schedule: "0 4 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: registry-garbage-collector
          volumes:
          - configMap:
              defaultMode: 420
              name: registry-config
            name: registry-config
          containers:
          - name: registry-garbage-collector
            image: gmelillo/registry:latest
            imagePullPolicy: Always
            env:
            - name: REGISTRY_STORAGE_S3_ACCESSKEY
              valueFrom:
                secretKeyRef:
                  key: s3AccessKey
                  name: registry-secret
            - name: REGISTRY_STORAGE_S3_SECRETKEY
              valueFrom:
                secretKeyRef:
                  key: s3SecretKey
                  name: registry-secret
            - name: REGISTRY_STORAGE_S3_REGION
              value: eu-wes-1
            - name: REGISTRY_STORAGE_S3_BUCKET
              value: registry.example.com
            - name: REGISTRY_STORAGE_S3_SECURE
              value: "true"
            - name: REGISTRY_STORAGE_DELETE_ENABLED
              value: "true"
            volumeMounts:
            - mountPath: /etc/docker/registry
              name: registry-config
          restartPolicy: OnFailure
```
