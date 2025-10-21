import { CfnOutput, Duration, RemovalPolicy, Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { Bucket } from 'aws-cdk-lib/aws-s3';
import { DockerImageCode, DockerImageFunction } from 'aws-cdk-lib/aws-lambda';
import { LogGroup, RetentionDays } from 'aws-cdk-lib/aws-logs';
import { Cors, EndpointType, LambdaIntegration, RestApi } from 'aws-cdk-lib/aws-apigateway';
import { Repository } from 'aws-cdk-lib/aws-ecr';

const uploadImageRepoArn = 'arn:aws:ecr:ap-northeast-1:910136156309:repository/upload-images-repo';
const inferenceRepoArn = 'arn:aws:ecr:ap-northeast-1:910136156309:repository/inference-repo';

interface MainStackProps extends StackProps {
    region: string;
}

export class MainStack extends Stack {
    constructor(scope: Construct, id: string, props: MainStackProps) {
        super(scope, id, props);

        // ECR
        const uploadImagesRepoName = 'upload-images-repo';
        const uploadImagesRepo = Repository.fromRepositoryArn(
            this,
            uploadImagesRepoName,
            uploadImageRepoArn,
        );
        const inferenceRepoName = 'inference-repo';
        const inferenceRepo = Repository.fromRepositoryArn(
            this,
            inferenceRepoName,
            inferenceRepoArn,
        );

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
                removalPolicy: RemovalPolicy.DESTROY,
            },
        );

        // Lambda (Docker image)
        const uploadDocumentLambdaFunctionName = 'upload-document';
        const uploadLambdaFunction = new DockerImageFunction(
            this,
            uploadDocumentLambdaFunctionName,
            {
                functionName: uploadDocumentLambdaFunctionName,
                code: DockerImageCode.fromEcr(uploadImagesRepo, { tagOrDigest: 'latest' }),
                environment: {
                    BUCKET_NAME: documentBucket.bucketName,
                    REGION: props.region,
                },
                timeout: Duration.seconds(29),
                logGroup: dockerImageLambdaFunctionLogGroup,
            },
        );
        documentBucket.grantPut(uploadLambdaFunction); // Lambda -> S3 (PUT Object)

        // Lambda (Docker image)
        const inferDocumentLambdaFunctionName = 'infer-document';
        const inferLambdaFunction = new DockerImageFunction(this, inferDocumentLambdaFunctionName, {
            functionName: inferDocumentLambdaFunctionName,
            code: DockerImageCode.fromEcr(inferenceRepo, { tagOrDigest: 'latest' }),
            environment: {
                BUCKET_NAME: documentBucket.bucketName,
            },
            timeout: Duration.seconds(29),
            logGroup: dockerImageLambdaFunctionLogGroup,
            memorySize: 1024,
        });
        documentBucket.grantRead(inferLambdaFunction); // Lambda -> S3 (Get Object)

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

        const uploadIntegration = new LambdaIntegration(uploadLambdaFunction, {
            timeout: Duration.seconds(20), // integration timeout APIGateway/Lambda
        });
        const inferenceIntegration = new LambdaIntegration(inferLambdaFunction, {
            timeout: Duration.seconds(29),
        });

        // resource
        const imageResource = restApi.root.addResource('image');
        const inferenceResource = restApi.root.addResource('infer');

        // API path definitions
        imageResource.addMethod('POST', uploadIntegration); // POST: /image
        inferenceResource.addMethod('POST', inferenceIntegration); // POST: /infer

        // API path
        new CfnOutput(this, 'api-base-url', {
            value: `https://${restApi.restApiId}.execute-api.${props.region}.amazonaws.com/${stageName}/`,
        });
    }
}
