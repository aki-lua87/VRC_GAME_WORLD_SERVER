import os
import boto3
import datetime
import random

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
    # パスコードのペアを作成する
    pub_passcode = create_passcode()
    priv_passcode = create_passcode()
    regist(pub_passcode, priv_passcode, world_id)
    # 公開パスコードを返す
    return {
        'statusCode': 200,
        'body': f'{pub_passcode}'
    }


def regist(pub_passcode: str, priv_passcode: str, world_id: str):
    table.put_item(
        Item={
            'attribute_name': 'vgws/passcode',
            'attribute_key': f'{world_id}_{pub_passcode}',
            'pub_passcode': pub_passcode,
            'priv_passcode': priv_passcode,
            'world_id': world_id,
            'status': 'created',
            'start_at': datetime.datetime.now().isoformat()
        }
    )


def create_passcode():
    # 4桁のランダムな数字を作成
    passcode = random.randint(1000, 9999)
    return passcode
