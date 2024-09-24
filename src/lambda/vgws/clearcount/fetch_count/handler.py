import os
import boto3
from boto3.dynamodb.conditions import Key
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE'])


def main(event, context):
    queryStringParameters = event.get('queryStringParameters')
    if queryStringParameters is None:
        return {
            'statusCode': 400,
            'body': 'queryStringParameters is required'
        }
    # TODO: VRCからのみのvalidation
    # eventのクエリ文字列からworld_idを取得する
    world_id = queryStringParameters.get('world_id')
    print('world_id:', world_id)
    datas = fetch(world_id)
    # datasを[{attribute_key}: {completion_count}] の形式で返却
    response = []
    for data in datas:
        count = data.get('completion_count')
        attribute_key = data.get('attribute_key')
        print(f'{attribute_key}: {count}')
        response.append({attribute_key: int(count)})
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }


def fetch(world_id: str):
    # プライマリキーがvgws_countup_{world_id}のレコードを取得し返却
    response = table.query(
        KeyConditionExpression=Key('attribute_name').eq(f'vgws_countup_{world_id}')
    )
    return response.get('Items')
