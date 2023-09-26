import json


def return400(message='bad request'):
    return {
        'headers': {
            "Access-Control-Allow-Origin": "*"
        },
        'statusCode': 400,
        'body': json.dumps(
            {
                'status': 'CANCELED',
                'error': message
            }
        )
    }


def return200():
    return {
        'headers': {
            "Access-Control-Allow-Origin": "*"
        },
        'statusCode': 200,
        'body': json.dumps(
            {
                'status': 'OK'
            }
        )
    }


def return200canncel():
    return {
        'headers': {
            "Access-Control-Allow-Origin": "*"
        },
        'statusCode': 200,
        'body': json.dumps(
            {
                'status': 'CANCELED'
            }
        )
    }