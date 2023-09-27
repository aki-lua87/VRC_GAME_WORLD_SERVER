import ddbutils
import httputils


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
    terminal = ddbutils.get_terminal(terminal_id)
    if terminal is None:
        print('entry is None')
        return httputils.return400()
    # action/checkのレスポンスがギブアップなら相手のギブアップと判定したい
    ddbutils.update_terminal_giveup(terminal_id)
    ddbutils.delete_stand_by(terminal_id)
    # マッチ情報取得
    match_id = terminal.get('match_id')
    if match_id is None or match_id == 'none':
        print('match_id is None')
        return httputils.return200()
    match = ddbutils.get_match(match_id)
    if match is None:
        print('match is None')
        return httputils.return400()
    print('match_giveup')
    ddbutils.match_giveup(match_id)
    return httputils.return200()
