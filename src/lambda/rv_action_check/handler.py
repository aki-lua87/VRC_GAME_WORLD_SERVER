import json

import ddbutils
import httputils


# rv_action_check 手取得
def main(event, context):
    print('event:', event)
    print('context:', context)
    queryStringParameters = event.get('queryStringParameters')
    if queryStringParameters is None:
        return httputils.return400()
    terminal_id = queryStringParameters.get('terminal_id', None)
    if terminal_id is None:
        return httputils.return400()
    # 端末情報取得
    entry = ddbutils.get_entry(terminal_id)
    if entry is None:
        return httputils.return400()
    # マッチ情報取得
    match_id = entry.get('match_id')
    if match_id is None:
        return httputils.return400()
    match = ddbutils.get_match(match_id)
    if match is None:
        return httputils.return400()
    # マッチ情報を返却
    return {
        'statusCode': 200,
        'body': json.dumps(match)
    }
