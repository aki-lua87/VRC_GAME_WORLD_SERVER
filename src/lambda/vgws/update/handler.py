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
    # world_id以外のクエリ文字列を取得
    other_query = {}
    for key in queryStringParameters:
        if key != 'world_id':
            other_query[key] = queryStringParameters[key]
    print('other_query:', other_query)
    # DynamoDBへ
    update(ip_hash, world_id, other_query)
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


def update(ip: str, world_id: str, other_query: dict):
    update_expression = 'SET end_at = :val1'
    expression_attribute_values = {
        ':val1': datetime.datetime.now().isoformat()
    }
    for key in other_query:
        update_expression += f', {key} = :{key}'
        expression_attribute_values[f':{key}'] = other_query[key]
    table.update_item(
        Key={
            'attribute_name': 'vgws',
            'attribute_key': f'{world_id}_{ip}',
        },
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values
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
