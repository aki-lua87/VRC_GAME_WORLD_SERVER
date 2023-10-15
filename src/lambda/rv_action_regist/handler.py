# import json

import ddbutils
import httputils
import datautils


# rv_regist_action
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
    action = queryStringParameters.get('action', None)
    if action is None:
        print('action is None')
        return httputils.return400()
    # 端末情報取得
    entry = ddbutils.get_terminal(terminal_id)
    if entry is None:
        print('terminal_id:', terminal_id)
        print('get_terminal is None')
        return httputils.return400()
    if entry.get('status') != datautils.STATUS_MATCHED:
        print('status is not MATCHED')
        return httputils.return200canncel()
    # マッチID取得
    match_id = entry.get('match_id')
    if match_id is None or match_id == 'none':
        print('match_id is None')
        return httputils.return200canncel()
    # actionを登録
    ddbutils.regist_action(match_id, terminal_id, action)
    # マッチ情報を返却
    match = ddbutils.get_match(match_id)
    response = datautils.ActionRegistResponse(match.get('status'), match.get('latest'), match.get('history'))
    # return
    return {
        'headers': {
            "Access-Control-Allow-Origin": "*"
        },
        'statusCode': 200,
        'body': datautils.responseJson(response)
    }
