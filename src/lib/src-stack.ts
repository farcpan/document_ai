import { CfnOutput, Duration, RemovalPolicy, Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { Bucket } from 'aws-cdk-lib/aws-s3';
import { DockerImageCode, DockerImageFunction } from 'aws-cdk-lib/aws-lambda';
import { LogGroup, RetentionDays } from 'aws-cdk-lib/aws-logs';
import { Cors, EndpointType, LambdaIntegration, RestApi } from 'aws-cdk-lib/aws-apigateway';

interface MainStackProps extends StackProps {
    region: string;
}

export class MainStack extends Stack {
    constructor(scope: Construct, id: string, props: MainStackProps) {
        super(scope, id, props);

        // S3 Bucket
        const bucketName = 'document-bucket-20251020';
        const documentBucket = new Bucket(this, bucketName, {
            bucketName: bucketName,
            removalPolicy: RemovalPolicy.DESTROY,
            autoDeleteObjects: true,
        });

        // LogGroup
        const dockerImageLambdaFunctionLogGroup = new LogGroup(
            this,
            'docker-image-lambda-loggroup',
            {
                logGroupName: 'docker-image-lambda-loggroup',
                retention: RetentionDays.ONE_DAY,
            },
        );

        // Lambda (Docker image)
        const uploadDocumentLambdaFunctionName = 'upload-document';
        const lambdaFunction = new DockerImageFunction(this, uploadDocumentLambdaFunctionName, {
            functionName: uploadDocumentLambdaFunctionName,
            code: DockerImageCode.fromImageAsset('lambdas/upload-images'), // directory in which Dockerfile exists
            environment: {
                BUCKET_NAME: documentBucket.bucketName,
                REGION: props.region,
            },
            timeout: Duration.seconds(29),
            logGroup: dockerImageLambdaFunctionLogGroup,
        });

        documentBucket.grantPut(lambdaFunction); // Lambda -> S3 (PUT Object)

        // API Gateway
        const restApiName = 'MyApi';
        const stageName: string = 'v1';
        const restApi = new RestApi(this, restApiName, {
            restApiName: restApiName,
            deployOptions: {
                stageName: stageName,
            },
            defaultCorsPreflightOptions: {
                allowOrigins: Cors.ALL_ORIGINS,
                allowMethods: Cors.ALL_METHODS,
                allowHeaders: Cors.DEFAULT_HEADERS,
                statusCode: 200,
            },
            endpointTypes: [EndpointType.REGIONAL],
        });

        const uploadIntegration = new LambdaIntegration(lambdaFunction, {
            timeout: Duration.seconds(20), // integration timeout APIGateway/Lambda
        });

        // resource
        const imageResource = restApi.root.addResource('image');

        // API path definitions
        imageResource.addMethod('POST', uploadIntegration); // POST: /image

        // API path
        new CfnOutput(this, 'api-base-url', {
            value: `https://${restApi.restApiId}.execute-api.${props.region}.amazonaws.com/${stageName}/`,
        });
    }
}
