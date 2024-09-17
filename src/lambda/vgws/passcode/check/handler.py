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
    # ワールドIDとパスコードからプライベートパスコードを取得する
    item = get_priv_passcode(world_id, pub_passcode)
    if item is None:
        return {
            'statusCode': 200,
            'body': 'NonePasscode'
        }
    # ステータスを確認し返却
    status = item.get('status')
    return {
        'statusCode': 200,
        'body': status
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
