# Development Environment

Some of the tools the project able to use needs specific systems installed to test a full end2end.
Here are the list of the installations that needed:

## Install Docker
`https://docs.docker.com/desktop/install/mac-install/`

### Install Minikube

https://minikube.sigs.k8s.io/docs/start/

For Mac just:    

```
brew install minikube
```

#### Start minikube
```
minikube start
```

### Create Jenkins on Minikube

Create the Jenkins deployment
```
kubectl create namespace jenkins
kubectl create -f jenkins-deployment.yaml -n jenkins
kubectl create -f jenkins-service.yaml -n jenkins
```

### Open Jenkins Server
```
minikube service jenkins -n jenkins
```
After installing Jenkins in the first time, the default admin password stored here:

```
kubectl exec --stdin --tty `kubectl get pods -n jenkins | awk '{if ($1 ~ "jenkins") print $0}' | awk '{print $1}'` -n jenkins -- cat /var/jenkins_home/secrets/initialAdminPassword
```

### Config those env vars:
```
export JENKINS_URL=http://127.0.0.1:51936
export JENKINS_USERNAME=<CHANGEME>    
export JENKINS_PASSWORD=<CHANGEME>    
```

### Create ArgoCD on Minikube

[Install the Argo CLI](https://github.com/argoproj/argo-workflows/releases/tag/v3.2.6) by GitHub releases, or in Mac by:
```
brew install argocd
```


```
kubectl create ns argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/v2.7.7/manifests/install.yaml
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-workflows/master/manifests/quick-start-postgres.yaml

```

Verify the installation by making sure the resources are in running state:

```
kubectl get all -n argocd
```

#### Open the ArgoCD server
```
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

Navigate to the [local server](https://localhost:8080). The default `username` is admin, and the default password can be accessed via:

```
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo
```

##### Note: you can login via CLI:

```
argocd login localhost:8080 --grpc-web
```

By default the `admin` user in Argo do not have privilege to access the API, so to be able doing it, you need to edit the ConfigMap by:

```
kubectl edit configmap argocd-cm --namespace argocd
```

Add to the ConfigMap:

```
data:
  accounts.admin: apiKey
```

If you want to add another user, you need to add it both to that ConfigMap, and add RBAC in that ConfigMap:

```
kubectl edit configmap argocd-rbac-cm --namespace argocd
```

Add to the previous one:

```
data:
  accounts.admin: apiKey
  accounts.myawesomeuser: login, apiKey
```
Add to the ConfigMap:

```
data:
  policy.csv: |
    g, myawesomeuser, role:admin
```

Once you are doing it, you can generate token or inside the [Argo UI](https://localhost:8080/settings/accounts/admin), or by using the CLI:

For `admin`:
```
argocd account generate-token
```

For `myawesomeuser`:
```
argocd account generate-token --account myawesomeuser
```

Take that generated token `ey....`, and configured it in environment variable, e.g:

```
export ARGO_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhcmdvY2QiLCJzdWIiOiJhZG1pbjphcGlLZXkiLCJuYmYiOjE2ODkxODgwNjUsImlhdCI6MTY4OTE4ODA2NSwianRpIjoiNzUxZjZjYzEtZTIyZC00N2JlLWI5Y2QtMjdjMWIwNmNjMmY4In0.OA0ItebqfjFxaPXnrlTXgPkrev28KNFC34ixTZjbuGU
```

You need to configure also the the Argo URL, and `development` in `PYTHON_ENV` environment variable so the TLS verification for the Argo server will not failed (self signed certificate):

```
export ARGO_URL=https://localhost:8080
export PYTHON_ENV=development
```

To test everything works as expected from API perspective, test the API by:


```
curl -k https://localhost:8080/api/version -H "Authorization: Bearer $ARGO_TOKEN"
```

You should see something like:

```
{"Version":"v2.5.8+bbe870f","BuildDate":"2023-01-25T16:17:52Z","GitCommit":"bbe870ff5904dd1cebeba6c5dcb7129ce7c2b5e2","GitTreeState":"clean","GoVersion":"go1.18.10","Compiler":"gc","Platform":"linux/arm64","KustomizeVersion":"v4.5.7 2022-08-02T16:35:54Z","HelmVersion":"v3.10.3+g835b733","KubectlVersion":"v0.24.2","JsonnetVersion":"v0.18.0"}
```

If you want to see all the swagger API of Argo, you can access it via that url: https://localhost:8080/swagger-ui

## Config OPA tool

### Install OPA

```
brew install opa
```

> **Note**
> To run the `opa` tool, you need to run the opa policies server:

`docker run -it --rm -p 8181:8181 openpolicyagent/opa run --server --addr :8181`

#### Test exmaple to run opa cli on the rego for a given data json example:
`opa eval --data genia/tools/opa/policies/k8s_policies.rego --input genia/tools/opa/policies/samples/k8s/running_containers_as_root.json "data"`

Note that you can get all the k8s resources in JSON format and write any policy you would like:

```
kubectl get all --all-namespaces -o yaml | yq -j
```

