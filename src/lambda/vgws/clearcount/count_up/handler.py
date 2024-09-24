import os
import boto3
import httputils

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE'])


def main(event, context):
    discord_webhook_url = os.environ['NAZOWA_URL']
    nazowa_id = os.environ['NAZPWA_ID']
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
    # eventのクエリ文字列からtargetを取得する
    target = queryStringParameters.get('target')
    print('target:', target)
    # validation
    if world_id is None:
        return {
            'statusCode': 400,
            'body': 'world_id is required'
        }
    if target is None:
        return {
            'statusCode': 400,
            'body': 'target is required'
        }
    count = upsert(world_id, target)
    if world_id == 'vwgs' or world_id == nazowa_id:
        # Discordに通知
        message = f'{target} がクリアされました。{count}グループ目のクリア者です。'
        httputils.postWebhook2(f'{message}', discord_webhook_url)
    return {
        'statusCode': 200,
        'body': str(count)
    }

# DynamoDBへUPSERT、レコードが存在する場合はcountをインクリメントし、countの値を返却


def upsert(world_id: str, target: str):
    response = table.get_item(
        Key={
            'attribute_name': f'vgws_countup_{world_id}',
            'attribute_key': f'{target}',
        }
    )
    item = response.get('Item')
    if item is None:
        table.put_item(
            Item={
                'attribute_name': f'vgws_countup_{world_id}',
                'attribute_key': f'{target}',
                'completion_count': 1
            }
        )
        return 1
    completion_count = item.get('completion_count')
    if completion_count is None:
        completion_count = 1
    else:
        completion_count += 1
    table.update_item(
        Key={
            'attribute_name': f'vgws_countup_{world_id}',
            'attribute_key': f'{target}',
        },
        UpdateExpression='SET completion_count = :val1',
        ExpressionAttributeValues={
            ':val1': completion_count
        }
    )
    return completion_count
