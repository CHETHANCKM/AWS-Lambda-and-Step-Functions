import json

print('Loading function')


def lambda_handler(event, context):
    try:
        print("Archiving the file")
        return event
    except Exception as e:
        print(e)
        return event
        raise e
