import json
import uuid

import ddbutils
import httputils


def main(event, context):
    print('event:', event)
    print('context:', context)
    queryStringParameters = event.get('queryStringParameters')
    if queryStringParameters is None:
        return httputils.return400()
    terminal_id = queryStringParameters.get('terminal_id', None)
    if terminal_id is None:
        return httputils.return400()
    # 登録
    ddbutils.regist_entry(terminal_id)
    # 待機確認
    stand_by = ddbutils.get_stand_by()
    if stand_by is None:
        # 待機登録
        ddbutils.regist_stand_by(terminal_id)
        return httputils.return200()
    # マッチング
    match_id = str(uuid.uuid4())
    ddbutils.regist_match(terminal_id, stand_by.get('attribute_key'), match_id)
    # マッチング結果通知
    return {
        'statusCode': 200,
        'body': json.dumps(
            {
                'result': 'MATCHED',
                'match_id': match_id
            }
        )
    }


# 既にマッチング中の場合に呼ばれると上書き
# 進行中放置などのプレイ不可を防ぐために上記のままにする
