#!/bin/bash

# exit when any command fails
set -e

# Check if helm is installed.
if ! command -v helm &> /dev/null
then
    echo "helm could not be found. Install it following this: https://helm.sh/docs/intro/install/"
    exit
fi

# https://docs.aws.amazon.com/eks/latest/userguide/calico.html
kubectl create namespace tigera-operator
helm repo add projectcalico https://docs.projectcalico.org/charts
helm repo update                         
helm install calico projectcalico/tigera-operator --version v3.24.1 -f calico/values.yaml --namespace tigera-operator