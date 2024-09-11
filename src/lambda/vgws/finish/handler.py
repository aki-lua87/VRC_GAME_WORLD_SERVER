import os
import boto3
import datetime
import json
import hashlib

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE'])


def main(event, context):
    # eventからIPアドレスを取得する
    ip = event.get('requestContext').get('identity').get('sourceIp')
    print('ip:', ip)
    # ipをハッシュ化する
    ip_hash = hashlib.sha256(ip.encode()).hexdigest()
    print('ip_hash:', ip_hash)
    # eventのクエリ文字列からworld_idを取得する
    queryStringParameters = event.get('queryStringParameters', {})
    world_id = queryStringParameters.get('world_id')
    print('world_id:', world_id)
    # validation
    if world_id is None:
        return {
            'statusCode': 400,
            'body': 'world_id is required'
        }
    # DynamoDBへ
    update(ip_hash, world_id)
    result_data = get(ip_hash, world_id)
    if result_data is None:
        return {
            'statusCode': 400,
            'body': 'No data'
        }
    return {
        'statusCode': 200,
        'body': json.dumps(result_data)
    }


def update(ip: str, world_id: str):
    table.update_item(
        Key={
            'attribute_name': 'vgws',
            'attribute_key': f'{world_id}_{ip}',
        },
        UpdateExpression='SET end_at = :val1',
        ExpressionAttributeValues={
            ':val1': datetime.datetime.now().isoformat()
        }
    )


def get(ip: str, world_id: str):
    response = table.get_item(
        Key={
            'attribute_name': 'vgws',
            'attribute_key': f'{world_id}_{ip}',
        }
    )
    record = response.get('Item')
    if record is None:
        return None
    return record
