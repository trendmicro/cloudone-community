import { expect as expectCDK, matchTemplate, MatchStyle } from '@aws-cdk/assert';
import * as cdk from 'aws-cdk-lib';
import * as FssFullScan from '../lib/fss-full-scan-stack';

test('Empty Stack', () => {
    const app = new cdk.App();
    // WHEN
    const stack = new FssFullScan.FssFullScanStack(app, 'MyTestStack');
    // THEN
    expectCDK(stack).to(matchTemplate({
      "Resources": {}
    }, MatchStyle.EXACT))
});
