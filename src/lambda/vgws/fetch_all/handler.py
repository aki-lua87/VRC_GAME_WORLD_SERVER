import os
import boto3
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
    result_data = get_all(ip_hash, world_id)
    if result_data is None:
        return {
            'statusCode': 400,
            'body': 'No data'
        }
    return {
        'statusCode': 200,
        'body': json.dumps(result_data)
    }


def get_all(ip: str, world_id: str):
    # PK = vgws
    # SK = {world_id}*
    # で検索する
    response = table.query(
        KeyConditionExpression='attribute_name = :val1 AND begins_with(attribute_key, :val2)',
        ExpressionAttributeValues={
            ':val1': 'vgws',
            ':val2': f'{world_id}_'
        }
    )
    records = response.get('Items')
    if records is None:
        return None
    return records
