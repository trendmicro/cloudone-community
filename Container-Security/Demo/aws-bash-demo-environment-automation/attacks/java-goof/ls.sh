#!/bin/bash

# exit when any command fails
set -e

COMMAND="ls"
URL="http://$(kubectl get svc -n demo --selector=app=java-goof -o jsonpath='{.items[*].status.loadBalancer.ingress[0].hostname}')"

kubectl run attacker --rm -i --tty --image raphabot/container-sec-attacker "$URL" $COMMAND