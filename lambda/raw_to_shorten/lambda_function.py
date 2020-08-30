# import the json utility package since we will be working with a JSON object
import json
# import the AWS SDK (for Python the package name is boto3)
import boto3
import hashlib
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
index_table = 'Indexing'
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

def put_to_table(table_name, shorten_url, raw_url):
    table = dynamodb.Table(table_name)
    table.put_item(
        Item={
            'URL': shorten_url,
            'raw': raw_url
            })
    return

def get_table_item(table_name, index):
    table = dynamodb.Table(table_name)
    item = table.get_item(Key={'URL': index}, ConsistentRead=True)
    return item

def get_md5_id(url):
    md5result = hashlib.md5(url.encode()).hexdigest()
    id = changeToTenBase(md5result,10)
    id = changeBase(id, 62)
    id = id[0:7]
    return id
    
# define the handler function that the Lambda service will use as an entry point
def lambda_handler(event, context):
    rawurlstr = event['url']
    id = get_md5_id(rawurlstr)
    response = get_table_item(index_table, id)
    if response.get('Item') == None:
        put_to_table(index_table, id, rawurlstr)
        return {
            'statusCode': 200,
            'body': json.dumps(id).strip('\"')
        }
    else:
        return {
        'statusCode': 301,
        'location': json.dumps(response['Item']['raw']).strip('\"')
        }
