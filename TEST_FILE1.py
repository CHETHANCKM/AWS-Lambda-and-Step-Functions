import json

def lambda_handler(event, context):
    # TODO implement
    print("Test file 1")
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
