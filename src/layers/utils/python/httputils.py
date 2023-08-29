import json


def return400():
    return {
        'statusCode': 400,
        'body': json.dumps(
            {
                'result': 'NG',
                'error': 'bad request'
            }
        )
    }


def return200():
    return {
        'statusCode': 200,
        'body': json.dumps(
            {
                'result': 'OK'
            }
        )
    }
