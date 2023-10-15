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
    matching_id = queryStringParameters.get('match_id', 'none')
    if matching_id is None:
        print('matching_id is None')
        return httputils.return400()
    # マッチ情報取得
    if matching_id is None or matching_id == 'none':
        print('match_id is None')
        return httputils.return200canncel()
    match = ddbutils.get_match(matching_id)
    if match is None:
        print('match is None')
        return httputils.return400()
    playerA = match.get('terminal_id_A')
    playerB = match.get('terminal_id_B')
    entryA = ddbutils.get_terminal(playerA)
    entryB = ddbutils.get_terminal(playerB)
    playerAname = entryA.get('user_name', 'anonymous')
    playerBname = entryB.get('user_name', 'anonymous')
    response = datautils.ActionHistoryResponse(match.get('status'), match.get('latest'), playerAname, playerBname, match.get('history'))
    # マッチ情報を返却
    return {
        'headers': {
            "Access-Control-Allow-Origin": "*"
        },
        'statusCode': 200,
        'body': datautils.responseJson(response)
    }
