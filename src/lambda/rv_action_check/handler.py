import datautils
import ddbutils
import httputils


# rv_action_check 手取得
def main(event, context):
    print('event:', event)
    queryStringParameters = event.get('queryStringParameters')
    if queryStringParameters is None:
        print('queryStringParameters is None')
        return httputils.return400()
    terminal_id = queryStringParameters.get('terminal_id', 'anonymous')
    app_id = queryStringParameters.get('app_id', 'anonymous')
    if terminal_id is None:
        print('terminal_id is None')
        return httputils.return400()
    if app_id == 'vrc':
        # プレフィクスとしてIPアドレスを付与
        terminal_id = event.get('requestContext').get('identity').get('sourceIp') + '_' + terminal_id
    # 端末情報取得
    entry = ddbutils.get_terminal(terminal_id)
    if entry is None:
        print('entry is None')
        return httputils.return400()
    # マッチ情報取得
    match_id = entry.get('match_id')
    if match_id is None or match_id == 'none':
        print('match_id is None')
        return httputils.return200canncel()
    match = ddbutils.get_match(match_id)
    if match is None:
        print('match is None')
        return httputils.return400()
    response = datautils.ActionGetResponse(match.get('status'), match.get('latest'), match.get('history'))
    # マッチ情報を返却
    return {
        'headers': {
            "Access-Control-Allow-Origin": "*"
        },
        'statusCode': 200,
        'body': datautils.responseJson(response)
    }
