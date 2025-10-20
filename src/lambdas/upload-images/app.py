import os
import json
import boto3

BUCKET_NAME = os.environ['BUCKET_NAME']
s3_client = boto3.client('s3')


def handler(event, context):
    body = json.loads(event.get('body', '{}'))
    dirname = body.get("dirname")
    filename = body.get("filename")


    # signed url
    url = s3_client.generate_presigned_url(
        'put_object',
        Params={'Bucket': BUCKET_NAME, 'Key': f"{dirname}/{filename}"},
        ExpiresIn=300   # 5min
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"url": url})
    }
