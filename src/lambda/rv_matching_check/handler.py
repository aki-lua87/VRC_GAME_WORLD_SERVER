import ddbutils
import httputils
import datautils


# rv_matching_check マッチングしてるかの確認
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
    # 取得
    entry = ddbutils.get_terminal(terminal_id)
    if entry is None:
        print('entry is None')
        return httputils.return200canncel()
    # スタンバイがあるか
    # stand_by = ddbutils.get_stand_by()
    # if stand_by is None:
    #     # スタンバイがない場合不正
    #     print('stand_by None')
    #     response = datautils.MatchingCheckResponse('ERROR', False, 'none', 'none')
    #     return {
    #         'headers': {
    #             "Access-Control-Allow-Origin": "*"
    #         },
    #         'statusCode': 200,
    #         'body': datautils.responseJson(response)
    #     }
    # マッチング取得
    match_id = entry.get('match_id')
    if match_id is None or match_id == 'none':
        # マッチング前基本レスポンス
        print('match_id is None 未マッチング')
        response = datautils.MatchingCheckResponse('ENTRYED', False, 'none', 'none')
        return {
            'headers': {
                "Access-Control-Allow-Origin": "*"
            },
            'statusCode': 200,
            'body': datautils.responseJson(response)
        }
    match = ddbutils.get_match(match_id)
    if match is None:
        # この時にマッチがないのは不正
        print('match is None')
        return httputils.return200canncel()
    # マッチのステータスが不正ならエラー
    status = match.get('status')
    if status != datautils.STATUS_MATCHED:
        print('status is おかしい', status)
        return httputils.return200canncel()
    # terminal_id_A が 自身と一致する場合先行フラグを建てる
    is_first = False
    opponent_terminal_id = 'none'
    if match.get('terminal_id_A', '') == terminal_id:
        is_first = True
        opponent_terminal_id = match.get('terminal_id_B', '')
    else:
        opponent_terminal_id = match.get('terminal_id_A', '')
    entry_aite = ddbutils.get_terminal(opponent_terminal_id)
    # 対戦相手の名前を取得
    opponent_name = entry_aite.get('user_name', 'anonymous')
    response = datautils.MatchingCheckResponse(match.get('status'), is_first, match_id, opponent_name)
    # マッチ後基本レスポンス
    return {
        'headers': {
            "Access-Control-Allow-Origin": "*"
        },
        'statusCode': 200,
        'body': datautils.responseJson(response)
    }
