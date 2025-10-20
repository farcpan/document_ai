import os
import json
import boto3
from botocore.config import Config

BUCKET_NAME = os.environ['BUCKET_NAME']
REGION = os.environ["REGION"]
s3_client = boto3.client(
    's3', 
    region_name=REGION, 
    config=Config(
        region_name=REGION,
        signature_version='s3v4',
        s3={'addressing_style': 'virtual'}, # important to force the endpoint hostname
    )
)


def handler(event, context):
    body = json.loads(event.get('body', '{}'))
    dirname = body.get("dirname")
    filename = body.get("filename")

    # signed url
    url = s3_client.generate_presigned_url(
        ClientMethod='put_object',
        HttpMethod='PUT',
        Params={'Bucket': BUCKET_NAME, 'Key': f"{dirname}/{filename}"},
        ExpiresIn=300   # 5min
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"url": url})
    }
