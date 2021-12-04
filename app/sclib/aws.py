import boto3
from botocore.exceptions import ClientError
import os
import uuid


def get_boto_client(service):

    params = {
        'aws_access_key_id': os.environ['SC_AWS_KEY'],
        'aws_secret_access_key': os.environ['SC_AWS_SECRET'],
        'region_name': 'us-east-1'
    }

    return boto3.client(service, **params)


def put_s3_item(image_path):

    object_key = f'change_images/{str(uuid.uuid4())}.png'            

    with open(image_path, mode='rb') as file:
        body = file.read()

    client = get_boto_client('s3')
    res = client.put_object(Body=body, Bucket='smart-carte-data', Key=object_key)
    print(res)

    return f'https://smart-carte-data.s3.amazonaws.com/{object_key}'

    

