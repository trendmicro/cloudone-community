import { expect as expectCDK, matchTemplate, MatchStyle } from '@aws-cdk/assert';
import * as cdk from '@aws-cdk/core';
import { ConformityToS3Stack } from '../lib/conformity-to-s3-stack';

// test('Empty Stack', () => {
//     const app = new cdk.App();
//     // WHEN
//     const stack = new ConformityToS3Stack(app, 'MyTestStack');
//     // THEN
//     expectCDK(stack).to(matchTemplate({
//       "Resources": {}
//     }, MatchStyle.EXACT))
// });
