import uuid

import datautils
import ddbutils
import httputils


def main(event, context):
    print('event:', event)
    queryStringParameters = event.get('queryStringParameters')
    if queryStringParameters is None:
        return httputils.return400()
    terminal_id = queryStringParameters.get('terminal_id', 'anonymous')
    app_id = queryStringParameters.get('app_id', 'anonymous')
    if app_id == 'vrc':
        # プレフィクスとしてIPアドレスを付与
        terminal_id = event.get('requestContext').get('identity').get('sourceIp') + '_' + terminal_id
    # 自身がマッチング中の場合はそのマッチングをキャンセル
    entry = ddbutils.get_entry(terminal_id)
    if entry is not None:
        status = entry.get('status')
        if status == 'MATCHED':
            ddbutils.match_cancel(entry.get('match_id'))
    # 登録
    ddbutils.regist_entry(terminal_id)
    # 待機確認
    stand_by = ddbutils.get_stand_by()
    if stand_by is None:
        # 待機登録
        ddbutils.regist_stand_by(terminal_id)
        print('regist_entry 待機登録')
        print('terminal_id:', terminal_id)
        return httputils.return200()
    # 自身が待機中の場合はマッチングしない
    if stand_by.get('attribute_key') == terminal_id:
        print('regist_entry 待機中')
        return httputils.return200()
    # マッチング
    match_id = str(uuid.uuid4())
    ddbutils.regist_match(stand_by.get('attribute_key'), terminal_id, match_id)
    response = datautils.EntryRegistResponse('MATCHED', match_id)
    print('regist_entry マッチング')
    print('terminal_id:', terminal_id)
    print('match_id:', match_id)
    # マッチング結果通知
    return {
        'headers': {
            "Access-Control-Allow-Origin": "*"
        },
        'statusCode': 200,
        'body': datautils.responseJson(response)
    }


# 既にマッチング中の場合に呼ばれると上書き
# 進行中放置などのプレイ不可を防ぐために上記のままにする
