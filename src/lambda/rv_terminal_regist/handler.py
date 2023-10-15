
import ddbutils
import httputils
import datautils


# 端末名登録
def main(event, context):
    print('event:', event)
    queryStringParameters = event.get('queryStringParameters')
    if queryStringParameters is None:
        return httputils.return400()
    terminal_id = queryStringParameters.get('terminal_id', 'anonymous')
    app_id = queryStringParameters.get('app_id', 'anonymous')
    name = queryStringParameters.get('name', 'anonymous')
    if app_id == 'vrc':
        # プレフィクスとしてIPアドレスを付与
        terminal_id = event.get('requestContext').get('identity').get('sourceIp') + '_' + terminal_id
    else:
        # VRC以外はダメ、いまのところ
        return httputils.return400()
    # 登録されているか
    terminal = ddbutils.get_terminal(terminal_id)
    if terminal is None:
        # 端末が登録されて無い場合は登録
        print('regist_terminal', terminal_id, name)
        ddbutils.regist_terminal(terminal_id, ddbutils.makeTTLdays(24), name, datautils.STATUS_STANDBY)
    else:
        # 端末が登録されている場合は更新
        print('update_terminal_name', terminal_id, name)
        ddbutils.update_terminal_name(terminal_id, name)
    return httputils.return200()
