import json

import ddbutils
import httputils


# rv_matching_check マッチングしてるかの確認
def main(event, context):
    print('event:', event)
    print('context:', context)
    queryStringParameters = event.get('queryStringParameters')
    if queryStringParameters is None:
        return httputils.return400()
    terminal_id = queryStringParameters.get('terminal_id', None)
    if terminal_id is None:
        return httputils.return400()
    # 取得
    entry = ddbutils.get_entry(terminal_id)
    if entry is None:
        print('entry is None')
        return httputils.return400()
    # マッチング取得
    match_id = entry.get('match_id')
    if match_id is None:
        print('match_id is None 未マッチング')
        return {
            'headers': {
                "Access-Control-Allow-Origin": "*"
            },
            'statusCode': 200,
            'body': json.dumps(entry)
        }
    match = ddbutils.get_match(match_id)
    if match is None:
        print('match is None')
        return httputils.return400()
    entry['terminal_id_A'] = match.get('terminal_id_A')
    entry['terminal_id_B'] = match.get('terminal_id_B')
    # 結果通知
    return {
        'headers': {
            "Access-Control-Allow-Origin": "*"
        },
        'statusCode': 200,
        'body': json.dumps(entry)
    }
