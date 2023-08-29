import os
import boto3
import datetime
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE'])


# 待機所(甘い仕様？)
def regist_stand_by(terminal_id):
    table.put_item(
        Item={
            'attribute_name': 'stand_by',
            'attribute_key': f'{terminal_id}',
            'updated_at': datetime.datetime.now().isoformat(),
        }
    )


def get_stand_by():
    response = table.query(
        KeyConditionExpression=Key('attribute_name').eq('stand_by')
    )
    records = response.get('Items')
    if len(records) == 0:
        return None
    return records[0]


# ## terminal_id schema
# attribute_name terminal_id
# attribute_key {terminal_id}
# status {ENTRYED, MATCHED, ENDED, CANCELED}
# match_id {match_id}
def get_entry(terminal_id):
    response = table.get_item(
        Key={
            'attribute_name': 'terminal_id',
            'attribute_key': f'{terminal_id}',
        }
    )
    record = response.get('Item')
    if record is None:
        return None
    return record


def regist_entry(terminal_id):
    table.put_item(
        Item={
            'attribute_name': 'terminal_id',
            'attribute_key': f'{terminal_id}',
            'status': 'ENTRYED',
            'updated_at': datetime.datetime.now().isoformat(),
        }
    )


# ## match_id schema
# attribute_name match_id
# attribute_key {match_id}
# terminal_id_A {terminal_id}
# terminal_id_B {terminal_id}
# history {terminal_id_A, terminal_id_B, terminal_id_A, terminal_id_B, ...}
# latest {terminal_id_A}
def regist_match(terminal_id_A, terminal_id_B, match_id):
    # 待機を削除
    table.delete_item(
        Key={
            'attribute_name': 'stand_by',
            'attribute_key': f'{terminal_id_A}',
        }
    )
    # マッチを登録
    table.put_item(
        Item={
            'attribute_name': 'match_id',
            'attribute_key': f'{match_id}',
            'terminal_id_A': f'{terminal_id_A}',
            'terminal_id_B': f'{terminal_id_B}',
            'history': [],
            'status': 'MATCHED',
            'updated_at': datetime.datetime.now().isoformat(),
        }
    )
    # ステータスを更新
    table.put_item(
        Item={
            'attribute_name': 'terminal_id',
            'attribute_key': f'{terminal_id_A}',
            'status': 'MATCHED',
            'match_id': f'{match_id}',
            'updated_at': datetime.datetime.now().isoformat(),
        }
    )
    table.put_item(
        Item={
            'attribute_name': 'terminal_id',
            'attribute_key': f'{terminal_id_B}',
            'status': 'MATCHED',
            'match_id': f'{match_id}',
            'updated_at': datetime.datetime.now().isoformat(),
        }
    )
    return match_id


def get_match(match_id):
    response = table.get_item(
        Key={
            'attribute_name': 'match_id',
            'attribute_key': f'{match_id}',
        }
    )
    record = response.get('Item')
    if record is None:
        return None
    return record


def match_cancel(match_id):
    match = get_match(match_id)
    if match is None:
        return None
    terminal_id_A = match.get('terminal_id_A')
    terminal_id_B = match.get('terminal_id_B')
    table.put_item(
        Item={
            'attribute_name': 'terminal_id',
            'attribute_key': f'{terminal_id_A}',
            'status': 'CANCELED',
            'match_id': f'{match_id}',
            'updated_at': datetime.datetime.now().isoformat(),
        }
    )
    table.put_item(
        Item={
            'attribute_name': 'terminal_id',
            'attribute_key': f'{terminal_id_B}',
            'status': 'CANCELED',
            'match_id': f'{match_id}',
            'updated_at': datetime.datetime.now().isoformat(),
        }
    )
    table.update_item(
        Key={
            'attribute_name': 'match_id',
            'attribute_key': f'{match_id}'
        },
        UpdateExpression="SET #status = :status",
        ExpressionAttributeNames={
            '#status': 'status'
        },
        ExpressionAttributeValues={
            ":status": 'CANCELED'
        }
    )


def regist_action(match_id, terminal_id, action):
    table.update_item(
        Key={
            'attribute_name': 'match_id',
            'attribute_key': f'{match_id}',
        },
        UpdateExpression="SET #h = list_append(#h, :value1), #l = :value2, #u = :value3",
        ExpressionAttributeNames={
            '#h': 'history',
            '#l': 'latest',
            '#u': 'updated_by'
        },
        ExpressionAttributeValues={
            ":value1": [action],
            ":value2": action,
            ":value3": terminal_id
        }
    )