#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { FssFullScanStack } from '../lib/fss-full-scan-stack';
import { DefaultStackSynthesizer } from 'aws-cdk-lib';

const app = new cdk.App();
new FssFullScanStack(app, 'FssFullScanStack', {
    synthesizer: new DefaultStackSynthesizer({
        generateBootstrapVersionRule: false,
        
    })
});
