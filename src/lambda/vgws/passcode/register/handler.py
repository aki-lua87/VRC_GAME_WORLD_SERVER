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
    # ループして重複しないようにする
    pub_passcode = create_passcode()
    for i in range(100):  # 100回まで
        # 生成したpub_passcodeが使われていないか確認
        item = get_passcode(world_id, pub_passcode)
        if item is not None:
            pub_passcode = create_passcode()
        else:
            break
    priv_passcode = create_passcode()  # こっちは重複していい
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
            'start_at': datetime.datetime.now().isoformat(),
            'TTL': ttlCreate()
        }
    )


def create_passcode():
    # 4桁のランダムな数字を作成
    passcode = random.randint(1000, 9999)
    return passcode


def get_passcode(world_id: str, pub_passcode: str):
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


def ttlCreate():
    start = datetime.datetime.now()
    expiration_date = start + datetime.timedelta(hours=1)
    return round(expiration_date.timestamp())
