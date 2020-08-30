import unittest
from lambda_function import *
import boto3
import hashlib
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb', region_name='us-west-2',)
index_table = 'Test_Indexing'

class TestRawToShorten(unittest.TestCase):
    def test_change_base(self):
        result = changeBase(1000000000, 62)
        self.assertEqual(result, '15ftgG')

    def test_change_to_ten_base(self):
        result = changeToTenBase('15ftgG', 62)
        self.assertEqual(result, 1000000000)
    
    def test_get_md5_id(self):
        result = get_md5_id("https://us-west-2.console.aws.amazon.com/lambda/home?region=us-west-2#/functions")
        self.assertEqual(result, '2BQivXW')
    
    def test_scenario(self):
        put_to_table(index_table, '2BQivXW', "https://us-west-2.console.aws.amazon.com/lambda/home?region=us-west-2#/functions")
        item = get_table_item(index_table, '2BQivXW')
        self.assertIsNotNone(item['Item'])
        self.assertEqual(item['Item']['URL'], '2BQivXW')
        self.assertEqual(item['Item']['raw'], "https://us-west-2.console.aws.amazon.com/lambda/home?region=us-west-2#/functions")

if __name__ == '__main__':
    unittest.main()