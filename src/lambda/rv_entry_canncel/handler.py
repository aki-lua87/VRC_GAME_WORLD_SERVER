import ddbutils
import httputils


def main(event, context):
    print('event:', event)
    queryStringParameters = event.get('queryStringParameters')
    if queryStringParameters is None:
        return httputils.return400()
    terminal_id = queryStringParameters.get('terminal_id', 'anonymous')
    app_id = queryStringParameters.get('app_id', 'anonymous')
    if terminal_id is None:
        return httputils.return400()
    if app_id == 'vrc':
        # プレフィクスとしてIPアドレスを付与
        terminal_id = event.get('requestContext').get('identity').get('sourceIp') + '_' + terminal_id
    # 端末情報取得
    entry = ddbutils.get_entry(terminal_id)
    if entry is None:
        return httputils.return400()
    # マッチ前なら削除
    if entry.get('status') == 'ENTRYED':
        ddbutils.delete_entry(terminal_id)
        ddbutils.delete_stand_by(terminal_id)
        return httputils.return200()
    # マッチ情報取得
    match_id = entry.get('match_id')
    if match_id is None:
        return httputils.return400()
    match = ddbutils.get_match(match_id)
    if match is None:
        return httputils.return400()
    # マッチをすべてキャンセル
    ddbutils.match_cancel(match_id)
    return httputils.return200()
