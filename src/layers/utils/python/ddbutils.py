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
            'registed_at': datetime.datetime.now().isoformat(),
            'TTL': ttlEntry()
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


def delete_stand_by(terminal_id):
    table.delete_item(
        Key={
            'attribute_name': 'stand_by',
            'attribute_key': f'{terminal_id}',
        }
    )


# ## terminal_id schema
# attribute_name terminal_id
# attribute_key {terminal_id}
# status {ENTRYED, MATCHED, ENDED, CANCELED}
# match_id {match_id}
def get_terminal(terminal_id):
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


def regist_terminal(terminal_id, TTL, user_name='anonymous'):
    table.put_item(
        Item={
            'attribute_name': 'terminal_id',
            'attribute_key': f'{terminal_id}',
            'match_id': 'none',
            'status': 'ENTRYED',
            'registed_at': datetime.datetime.now().isoformat(),
            'TTL': TTL,
            'user_name': user_name
        }
    )


def delete_terminal(terminal_id):
    table.delete_item(
        Key={
            'attribute_name': 'terminal_id',
            'attribute_key': f'{terminal_id}',
        }
    )


def update_terminal_matching(terminal_id, match_id):
    table.update_item(
        Key={
            'attribute_name': 'terminal_id',
            'attribute_key': f'{terminal_id}'
        },
        UpdateExpression="SET #status = :status, #match_id = :match_id",
        ExpressionAttributeNames={
            '#status': 'status',
            '#match_id': 'match_id'
        },
        ExpressionAttributeValues={
            ":status": 'MATCHED',
            ":match_id": f'{match_id}'
        }
    )


def update_terminal_cancel(terminal_id):
    table.update_item(
        Key={
            'attribute_name': 'terminal_id',
            'attribute_key': f'{terminal_id}'
        },
        UpdateExpression="SET #status = :status, #match_id = :match_id",
        ExpressionAttributeNames={
            '#status': 'status',
            '#match_id': 'match_id'
        },
        ExpressionAttributeValues={
            ":status": 'CANCELED',
            ":match_id": 'none'
        }
    )


def update_terminal_entry(terminal_id):
    table.update_item(
        Key={
            'attribute_name': 'terminal_id',
            'attribute_key': f'{terminal_id}'
        },
        UpdateExpression="SET #status = :status, #match_id = :match_id",
        ExpressionAttributeNames={
            '#status': 'status',
            '#match_id': 'match_id'
        },
        ExpressionAttributeValues={
            ":status": 'ENTRYED',
            ":match_id": 'none'
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
    delete_stand_by(terminal_id_A)
    # マッチを登録
    table.put_item(
        Item={
            'attribute_name': 'match_id',
            'attribute_key': f'{match_id}',
            'terminal_id_A': f'{terminal_id_A}',
            'terminal_id_B': f'{terminal_id_B}',
            'history': [],
            'latest': '',
            'status': 'MATCHED',
            'registed_at': datetime.datetime.now().isoformat(),
            'TTL': makeTTLdays(14)
        }
    )
    # ステータスを更新
    update_terminal_matching(terminal_id_A, match_id)
    update_terminal_matching(terminal_id_B, match_id)
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
    update_terminal_cancel(terminal_id_A)
    update_terminal_cancel(terminal_id_B)
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


def ttlEntry():
    start = datetime.datetime.now()
    expiration_date = start + datetime.timedelta(minutes=45)
    return round(expiration_date.timestamp())


def makeTTLdays(days):
    start = datetime.datetime.now()
    expiration_date = start + datetime.timedelta(days=days)
    return round(expiration_date.timestamp())


def makeTTLhours(hours):
    start = datetime.datetime.now()
    expiration_date = start + datetime.timedelta(hours=hours)
    return round(expiration_date.timestamp())
