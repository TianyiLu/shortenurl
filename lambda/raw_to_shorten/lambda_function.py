# import the json utility package since we will be working with a JSON object
import json
# import the AWS SDK (for Python the package name is boto3)
import boto3
import hashlib
from botocore.exceptions import ClientError

# create a DynamoDB object using the AWS SDK
dynamodb = boto3.resource('dynamodb')
# use the DynamoDB object to select our table
table = dynamodb.Table('ShortenURLDatabase')
counter_table = dynamodb.Table('AtomicCounter')
index_table = dynamodb.Table('Indexing')
baseList = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

def changeBase(n,b):
    x,y = divmod(n,b)
    if x>0:
        return changeBase(x,b) + baseList[y]
    else:             
        return baseList[y]

def changeToTenBase(s,b):
    sL = list(s)
    sL.reverse()
    result = 0
    for x in range(len(sL)):
        result = result + baseList.index(sL[x])*(b**x)
    return result


# define the handler function that the Lambda service will use as an entry point
def lambda_handler(event, context):

    rawurlstr = event['url']
    md5result = hashlib.md5(rawurlstr.encode()).hexdigest()
    id = changeToTenBase(md5result,10)
    
    response = table.get_item(Key={'ID': str(id)})
    if response.get('Item') == None:
        # if not found, atomic counter add 1
        response_c = counter_table.update_item(
            Key={
                'Name': "Counter"
            },
            UpdateExpression="set CurrentValue = (CurrentValue + :val)",
            ExpressionAttributeValues={
                ':val': 1
            },
            ReturnValues="UPDATED_NEW"
        )
        shorten_url = changeBase(int(response_c['Attributes']['CurrentValue']),62)
        while (len(shorten_url) < 7):
            shorten_url = '0'+ shorten_url
        # Write to the shorten_url table
        response_s = table.put_item(
        Item={
            'ID': str(id),
            'raw': rawurlstr,
            'shortenurl':shorten_url
            })
        response_i = index_table.put_item(
        Item={
            'URL': shorten_url,
            'raw': rawurlstr
            })
        return {
            'statusCode': 200,
            'body': json.dumps(shorten_url.strip('\"')).strip('\"')
        }
    else:
        response_i = index_table.put_item(
        Item={
            'URL': response['Item']['shortenurl'],
            'raw': rawurlstr
            })
        return {
        'statusCode': 200,
        'body': json.dumps(response['Item']['shortenurl']).strip('\"')
    }
    
    
