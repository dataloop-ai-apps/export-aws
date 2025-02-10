import dtlpy as dl
import logging
import base64
import boto3
import json
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name='AWS Export & Import')


class AWSExport(dl.BaseServiceRunner):
    def __init__(self):
        """
        Initializes the ServiceRunner with AWS Export & Import API credentials.
        """
        self.logger = logger
        self.logger.info('Initializing AWS Export & Import API client')
        raw_credentials = os.environ.get("AWS_INTEGRATION", None)
        if raw_credentials is None:
            raise ValueError(f"Missing AWS integration.")

        try:
            decoded_credentials = base64.b64decode(raw_credentials).decode("utf-8")
            credentials = json.loads(decoded_credentials)
        except Exception:
            raise ValueError(f"Failed to decode the service integration. Refer to the guide for proper AWS "
                             f"integrations usage with Dataloop: "
                             f"https://github.com/dataloop-ai-apps/export-aws/blob/main/README.md")
        self.aws_secret_access_key = credentials['secret']
        self.aws_access_key_id = credentials['key']

    def export_annotation(self, item: dl.Item, context: dl.Context):
        if context is not None and context.node is not None and 'customNodeConfig' in context.node.metadata:
            bucket_name = context.node.metadata['customNodeConfig']['bucket_name']
            region_name = context.node.metadata['customNodeConfig']['region_name']
            aws_rekognition_keys = {'region_name': region_name,
                                    'aws_access_key_id': self.aws_access_key_id,
                                    'aws_secret_access_key': self.aws_secret_access_key}

            logger.info('Bucket name set to: {}'.format(bucket_name))
        else:
            raise ValueError("Node configration in context is missing, can't determinate the bucket name")

        annotation_json = item.to_json()
        annotation_json['annotations'] = item.annotations.list().to_json()['annotations']
        filename, _ = os.path.splitext(item.filename)
        s3 = boto3.client("s3", **aws_rekognition_keys)
        filename = f"{filename[1:]}.json"
        s3.put_object(Bucket=bucket_name, Key=filename, Body=json.dumps(annotation_json))
        print(f"File {filename} uploaded to {bucket_name}/{filename}")

        return item

    def import_annotation(self, item: dl.Item, context: dl.Context):
        if context is not None and context.node is not None and 'customNodeConfig' in context.node.metadata:
            bucket_name = context.node.metadata['customNodeConfig']['bucket_name']
            region_name = context.node.metadata['customNodeConfig']['region_name']
            aws_rekognition_keys = {'region_name': region_name,
                                    'aws_access_key_id': self.aws_access_key_id,
                                    'aws_secret_access_key': self.aws_secret_access_key}

            logger.info('Bucket name set to: {}'.format(bucket_name))
        else:
            raise ValueError("Node configration in context is missing, can't determinate the bucket name")

        s3 = boto3.client("s3", **aws_rekognition_keys)
        filename, _ = os.path.splitext(item.filename)
        filename = f"{filename[1:]}.json"
        response = s3.get_object(Bucket=bucket_name, Key=filename)
        json_data = response['Body'].read().decode('utf-8')
        data = json.loads(json_data)
        item.annotations.upload(annotations=data['annotations'])
        return item
