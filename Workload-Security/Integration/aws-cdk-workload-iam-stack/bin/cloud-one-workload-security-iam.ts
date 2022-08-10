#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from '@aws-cdk/core';
import { CloudOneWorkloadSecurityIamStack } from '../lib/cloud-one-workload-security-iam-stack';

const app = new cdk.App();
new CloudOneWorkloadSecurityIamStack(app, 'CloudOneWorkloadSecurityIamStack');
