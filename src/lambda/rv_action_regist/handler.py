# import json

import ddbutils
import httputils


# rv_regist_action
def main(event, context):
    print('event:', event)
    print('context:', context)
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
        return httputils.return400()
    # 端末情報取得
    entry = ddbutils.get_entry(terminal_id)
    if entry is None:
        return httputils.return400()
    # マッチID取得
    match_id = entry.get('match_id')
    if match_id is None:
        return httputils.return400()
    # actionを登録
    ddbutils.regist_action(match_id, terminal_id, action)
    # return
    return httputils.return200()
