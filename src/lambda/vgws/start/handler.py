import os
import boto3
import datetime
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
    queryStringParameters = event.get('queryStringParameters')
    if queryStringParameters is None:
        return {
            'statusCode': 400,
            'body': 'queryStringParameters is required'
        }
    world_id = queryStringParameters.get('world_id')
    print('world_id:', world_id)
    # eventのクエリ文字列からforce=trueを取得する
    force = queryStringParameters.get('force')
    print('force:', force)
    # validation
    if world_id is None:
        return {
            'statusCode': 400,
            'body': 'world_id is required'
        }
    user_exists = is_user_exist(ip_hash, world_id)
    if user_exists and force != 'true':
        return {
            'statusCode': 400,
            'body': 'Already exists'
        }
    # DynamoDBへ
    regist(ip_hash, world_id)
    return {
        'statusCode': 200,
        'body': 'OK'
    }


def regist(ip: str, world_id: str):
    table.put_item(
        Item={
            'attribute_name': 'vgws',
            'attribute_key': f'{world_id}_{ip}',
            'start_at': datetime.datetime.now().isoformat()
        }
    )


def is_user_exist(ip: str, world_id: str):
    response = table.get_item(
        Key={
            'attribute_name': 'vgws',
            'attribute_key': f'{world_id}_{ip}',
        }
    )
    record = response.get('Item')
    if record is None:
        return False
    return True
