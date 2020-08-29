# import the json utility package since we will be working with a JSON object
import json
# import the AWS SDK (for Python the package name is boto3)
import boto3
import hashlib
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
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

def put_to_indexing(shorten_url, raw_url):
    index_table.put_item(
        Item={
            'URL': shorten_url,
            'raw': raw_url
            })
    return

def atomic_incr():
    response = counter_table.update_item(
            Key={
                'Name': "Counter"
            },
            UpdateExpression="set CurrentValue = (CurrentValue + :val)",
            ExpressionAttributeValues={
                ':val': 1
            },
            ReturnValues="UPDATED_NEW"
        )
    return int(response['Attributes']['CurrentValue'])
    
def put_to_shorten_table(id, raw_url, shorten_url):
    # Write to the shorten_url table
    response_s = table.put_item(
        Item={
            'ID': str(id),
            'raw': raw_url,
            'shortenurl':shorten_url
            })
    return

def shorten(num):
    url = changeBase(int(num),62)
    while (len(url) < 7):
        url = '0'+ url
    return url

def get_md5_id(url):
    md5result = hashlib.md5(url.encode()).hexdigest()
    id = changeToTenBase(md5result,10)
    return id
    
# define the handler function that the Lambda service will use as an entry point
def lambda_handler(event, context):
    rawurlstr = event['url']
    id = get_md5_id(rawurlstr)
    response = table.get_item(Key={'ID': str(id)})
    
    if response.get('Item') == None:
        counter = atomic_incr()
        shorten_url = shorten(counter)
        put_to_shorten_table(id, rawurlstr, shorten_url)
        put_to_indexing(shorten_url, rawurlstr)
        return {
            'statusCode': 200,
            'body': json.dumps(shorten_url.strip('\"')).strip('\"')
        }
    else:
        put_to_indexing(shorten_url, rawurlstr)
        return {
            'statusCode': 200,
            'body': json.dumps(response['Item']['shortenurl']).strip('\"')
    }
    
    
