import json
# import the AWS SDK (for Python the package name is boto3)
import boto3

# create a DynamoDB object using the AWS SDK
dynamodb = boto3.resource('dynamodb')
index_table = dynamodb.Table('Indexing')

def lambda_handler(event, context):

    response = index_table.get_item(Key={'URL': event['shortenurl']}, ConsistentRead=True)
    if response.get('Item') == None:
        return {
        'statusCode': 404,
        'statusDescription': 'Raw URL Not Found. Please try to contact system administrator shorten the raw url again. If the problem still existing, please contact AWS support center.',
        }
    else:
        return {
        'statusCode': 301,
        'location': json.dumps(response['Item']['raw']).strip('\"')
        }