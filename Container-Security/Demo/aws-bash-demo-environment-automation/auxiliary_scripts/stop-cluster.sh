#!/bin/bash

# Reads the cluster name
CLUSTER_NAME=$(cat .container-security-demo)

eksctl delete cluster "$CLUSTER_NAME"
