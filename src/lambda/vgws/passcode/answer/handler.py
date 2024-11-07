import os
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE'])


def main(event, context):
    # eventのクエリ文字列からworld_idを取得する
    queryStringParameters = event.get('queryStringParameters')
    if queryStringParameters is None:
        return {
            'statusCode': 400,
            'body': 'queryStringParameters is required'
        }
    world_id = queryStringParameters.get('world_id')
    print('world_id:', world_id)
    pub_passcode = queryStringParameters.get('passcode')
    # pri_passcode = queryStringParameters.get('pri_passcode') ローカルでチェックする！！！ 10000^2のURLが必要になるので
    # ワールドIDとパスコードからプライベートパスコードを取得する
    item = get_priv_passcode(world_id, pub_passcode)
    if item is None:
        return {
            'statusCode': 200,
            'body': 'NonePasscode'
        }
    # ステータスを確認しcreatedでなければエラー
    status = item.get('status')
    if status == 'prosessing':
        # ステータスを更新する
        update_status(world_id, pub_passcode)
        return {
            'statusCode': 200,
            'body': 'Congratulations'
        }
    elif status == 'complete':
        return {
            'statusCode': 200,
            'body': "AlreadyComplete"
        }
    elif status == 'created':
        # ステータスを更新する
        # 一足飛びパターン
        update_status(world_id, pub_passcode)
        # 成功を通知
        return {
            'statusCode': 200,
            'body': 'Congratulations'
        }
    else:
        return {
            'statusCode': 200,
            'body': "BadStatus"
        }


def get_priv_passcode(world_id: str, pub_passcode: str):
    response = table.get_item(
        Key={
            'attribute_name': 'vgws/passcode',
            'attribute_key': f'{world_id}_{pub_passcode}'
        }
    )
    item = response.get('Item')
    if item is None:
        return None
    return item


def update_status(world_id: str, pub_passcode: str):
    table.update_item(
        Key={
            'attribute_name': 'vgws/passcode',
            'attribute_key': f'{world_id}_{pub_passcode}'
        },
        UpdateExpression='SET #status = :status',
        ExpressionAttributeNames={
            '#status': 'status'
        },
        ExpressionAttributeValues={
            ':status': 'complete'
        }
    )
