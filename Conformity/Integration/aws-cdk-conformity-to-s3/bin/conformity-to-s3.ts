#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from '@aws-cdk/core';
import { ConformityToS3Stack } from '../lib/conformity-to-s3-stack';

const app = new cdk.App();
new ConformityToS3Stack(app, 'ConformityToS3Stack');
