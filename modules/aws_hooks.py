import dtlpy as dl
import logging
import base64
import boto3
import json
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name='AWS Export & Import')


class AWSExport(dl.BaseServiceRunner):
    def __init__(self, integration_name):

        aws_credentials = os.environ.get(integration_name.replace('-', '_'))
        decoded_bytes = base64.b64decode(aws_credentials)
        aws_credentials = decoded_bytes.decode("utf-8")
        aws_credentials = json.loads(aws_credentials)

        self.aws_secret_access_key = aws_credentials['secret']
        self.aws_access_key_id = aws_credentials['key']

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


def test():
    class Node:
        def __init__(self, metadata):
            self.metadata = metadata

    service_runner = AWSExport(integration_name="")
    original_item = dl.items.get(item_id='')
    original_annotations = original_item.annotations.list()
    remote_filepath = "/clones/1.jpg"
    try:
        item = original_item.dataset.items.get(filepath=remote_filepath)
        item.delete()
    except dl.exceptions.NotFound:
        pass

    item = original_item.clone(remote_filepath=remote_filepath)
    context = dl.Context()
    context._node = Node(metadata={'customNodeConfig': {'bucket_name': '', 'region_name': ''}})
    service_runner.export_annotation(item=item, context=context)
    item.annotations.delete(filters=dl.Filters(resource=dl.FiltersResource.ANNOTATION))
    service_runner.import_annotation(item=item, context=context)
    assert len(item.annotations.list()) == len(original_annotations)


if __name__ == '__main__':
    test()
