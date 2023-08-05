![PyPI](https://img.shields.io/pypi/v/sceptre-eks-lb-resolver?color=blue)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/sceptre-eks-lb-resolver)
[![CI/CD](https://github.com/pantuza/sceptre-eks-lb-resolver/actions/workflows/main.yaml/badge.svg)](https://github.com/pantuza/sceptre-eks-lb-resolver/actions/workflows/main.yaml)
![PyPI - Downloads](https://img.shields.io/pypi/dm/sceptre-eks-lb-resolver)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/sceptre-eks-lb-resolver.svg)](https://pypi.python.org/pypi/sceptre-eks-lb-resolver/)
[![PyPI license](https://img.shields.io/pypi/l/sceptre-eks-lb-resolver.svg)](https://pypi.python.org/pypi/sceptre-eks-lb-resolver/)

# sceptre-eks-lb-resolver
[Sceptre](https://github.com/Sceptre/sceptre) custom [resolver](https://sceptre.cloudreach.com/2.4.0/docs/resolvers.html#custom-resolvers) you can 
use to dynamically read [AWS EKS](https://aws.amazon.com/eks/) Load Balancer URI into your Sceptre [config](https://sceptre.cloudreach.com/2.3.0/docs/stack_config.html). 

It reads [services](https://kubernetes.io/docs/concepts/services-networking/service/) inside your Kubernetes cluster with type `LoadBalancer` and returns its External DNS/URI.


## Installation

```bash
$> pip install sceptre-eks-lb-resolver
```


## Usage

Simply call the resolver inside your Sceptre configuration files:

```yaml
template_path: mystack.yaml

parameters:
  ProjectName: "My k8s API"
  LoadBalancerURI: !eks_lb_uri -n backend -s data_api 
```

Will resolve to something like:

```yaml
LoadBalancerURI: "XXXXXXXXXXX.us-east-1.elb.amazonaws.com"
```

You can use your Sceptre [variables](https://sceptre.cloudreach.com/2.4.0/docs/stack_group_config.html#var) as arguments for the resolver:

```yaml
  ...
  LoadBalancerURI: !eks_lb_uri -n {{ var.namespace }} -s {{ var.service }}
```

So with that in place, when you run `sceptre launch --yes dev/us-east-1`, it
will call the resolver and assign the k8s load balancer URI to the Sceptre
variable `LoadBalancerURI` at runtime.

> Make sure to guarantee that you are properly authenticated within AWS



## Syntax

Resolver expects two arguments: `-n | --namespace` and `-s | --service-name`.
The `--namespace` argument is optional. It assumes kubeernetes `default` namespace
as its default value. 

All available ways of using this resolver are as follows:

```yaml
  LBArn: !eks_lb_uri --namespace {{ var.namespace }} --service-name {{ var.service }}
  LBArn: !eks_lb_uri -n {{ var.namespace }} -s {{ var.service }}
  LBArn: !eks_lb_uri -s {{ var.service }}  # Assumes default namespace
  LBArn: !eks_lb_uri -s "my_api_service_name"
  LBArn: !eks_lb_uri -n backend -s data_api
```


## How does it works?

The resolver is called by Sceptre in order to retrieve remote k8s cluster services.
The EKS Load Balancer Resolver uses kubernetes python client to connect on the remote
cluster and retrieve data of the given service name from a given namespace.

The K8s Load Balancer URI resolver simply tries to get the Load Balancer DNS as if you run:

```bash
$> kubectl --namespace backend get service api-service
NAME               TYPE           CLUSTER-IP       EXTERNAL-IP                               PORT(S)         AGE
api-service        LoadBalancer   10.0.42.123      XXXXXXXXXXX.us-east-1.elb.amazonaws.com   443:32214/TCP   12h40m
```

The resolver goes after the `XXXXXXXXXXX.us-east-1.elb.amazonaws.com` value. When succeeds, it loads in place this
value in your Sceptre template.


## Notes

Be aware that the shell which sceptre will be called MUST be authenticated on AWS and 
your kubeconfig properly updated to point to your AWS EKS remote cluster.

You can refer to the following links for either AWS and Kubernetes authentication:

* [AWS CLI Configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html)
* [AWS EKS Kubeconfig setup](https://docs.aws.amazon.com/eks/latest/userguide/create-kubeconfig.html)


## Contributing

Fork, change, make test, make check, Pull Request.
I will review the code and if Github Actions pipeline succeeds: congratulations! We are going to merge ;)
