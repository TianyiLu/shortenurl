import json
# import the AWS SDK (for Python the package name is boto3)
import boto3

# create a DynamoDB object using the AWS SDK
dynamodb = boto3.resource('dynamodb')
index_table = dynamodb.Table('Indexing')

def lambda_handler(event, context):
    response = index_table.get_item(Key={'URL': event['shortenurl']})
    if response.get('Item') == None:
        return {
        'statusCode': 404,
        'statusDescription': 'Not Found',
        }
    else:
        return {
        'statusCode': 301,
        'location': json.dumps(response['Item']['raw']).strip('\"')
        }