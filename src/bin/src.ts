#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { MainStack } from '../lib/src-stack';

const app = new cdk.App();

// region
const region = 'ap-northeast-1';

new MainStack(app, 'MainStack', {
    env: {
        region: region,
    },
    region: region,
});
