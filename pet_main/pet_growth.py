import json
import boto3
from boto3.dynamodb.conditions import Attr
from common import CommonConfig


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(CommonConfig.pet_child_tablename)

def view_growth_search_handler(event):
    # Initialize a session using Amazon DynamoDB

    # sk_user_id=a1f32dba-a001-7048-27f4-c088d1242f4a
    # Extract query parameters safely
    query_params = event.get('queryStringParameters', {})
    birth_id = query_params.get('birth_id')
    
    if not birth_id:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'statusCode': "400",
                "body":{
                'message': 'birth_id is required'
                }
               
            }),
            "isBase64Encoded": False
        }
    
    # Perform a query on the DynamoDB table
    response = table.scan(
        FilterExpression=Attr('birth_id').eq(birth_id) & Attr('day45').ne(None)  & Attr('day30').ne(None)  & Attr('day15').ne(None)  ,
    )
    
    # Extract items from the response
    items = response.get('Items', [])
    #to test the response numbers
    # item_count = len(items)
    
    # Return the response with status code 200 and items as body
    if not items:
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'statusCode': "404",
                'message': 'No items found'
            }),
            "isBase64Encoded": False
        }
    def decimal_default(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'statusCode': "200",
            'body': items[0]
        }, default=decimal_default),
        "isBase64Encoded": False
    }

def view_growth_list_handler(event):
    # Initialize a session using Amazon DynamoDB

    # sk_user_id=a1f32dba-a001-7048-27f4-c088d1242f4a
    # Extract query parameters safely
    query_params = event.get('queryStringParameters', {})
    sk_user_id = query_params.get('sk_user_id')
    
    if not sk_user_id:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'statusCode': "400",
                "body":{
                'message': 'user_id is required'
                }
               
            }),
            "isBase64Encoded": False
        }
    
    # Perform a query on the DynamoDB table
    response = table.scan(
        FilterExpression=Attr('sk_user_id').eq(sk_user_id) & Attr('day45').ne(None)  & Attr('day30').ne(None)  & Attr('day15').ne(None)  & Attr('day0').ne(None) ,
    )
    
    # Extract items from the response
    items = response.get('Items', [])
    #to test the response numbers
    # item_count = len(items)
    
    # Return the response with status code 200 and items as body
    # return {
    #     'statusCode': 200,
    #     'body': json.dumps(items)
    # }
    if not items:
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'statusCode': "404",
                'message': 'No items found'
            }),
            "isBase64Encoded": False
        }
    def decimal_default(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError
        
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'statusCode': "200",
            'body': items
        }, default=decimal_default),
        "isBase64Encoded": False
    }