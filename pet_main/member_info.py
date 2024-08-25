import json
import boto3
from boto3.dynamodb.conditions import Attr
from decimal import Decimal
from common import CommonConfig
from datetime import datetime
    
    
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(CommonConfig.pet_user_tablename)

def user_details_handler(event):
    # Initialize a session using Amazon DynamoDB

    
    # Extract query parameters safely
    query_params = event.get('queryStringParameters', {})
    user_id = query_params.get('user_id')
    
    if not user_id:
        return {
            'statusCode': 200,
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
    
    # Start building the filter expression with user_id
    filter_expression = Attr('pk_user_id').eq(user_id)
    
    # Add additional conditions if they are not None
    conditions_present = False
    
    # if sk_type is not None:
    #     filter_expression = filter_expression & Attr('sk_type').eq(sk_type)
    #     conditions_present = True
    
    # if status is not None:
    #     filter_expression = filter_expression & Attr('status').eq(status)
    #     conditions_present = True
    
    # # If no additional conditions are provided, add user_sk condition
    # if not conditions_present:
    #     filter_expression = filter_expression & Attr('sk_id').eq("sk#user_details")
    
    scan_params = {
        'FilterExpression': filter_expression
    }
    
    # Perform the scan operation
    response = table.scan(**scan_params)
    
    # Process the response
    items = response.get('Items', [])
    
    
    # Custom encoder for Decimal objects
    def decimal_default(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError
        
    if not conditions_present:
        items = items[0]
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

def member_list_handler(event):
    # Extract query parameters safely
    query_params = event.get('queryStringParameters', {})
    sk_id = query_params.get('sk_id')
    gender = query_params.get('gender')
    child_type = query_params.get('child_type')
    child_variety = query_params.get('child_variety')
    child_status = query_params.get('child_status')
    
    if not sk_id:
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'statusCode': "400",
                'message': 'sk_id is required'
            }),
            "isBase64Encoded": False
        }
    
    # Start building the filter expression with user_id
    filter_expression = Attr('sk_id').eq(sk_id)
    
    # Add additional conditions if they are not None
  
    
    # if gender is not None:
    #     filter_expression = filter_expression & Attr('gender').eq(gender)
    
    # if child_type is not None:
    #     filter_expression = filter_expression & Attr('child_type').eq(child_type)
  
    
    # if child_variety is not None:
    #     filter_expression = filter_expression & Attr('child_variety').eq(child_variety)
   
    
    # if child_status is not None:
    #     filter_expression = filter_expression & Attr('child_status').eq(child_status)
     
    
    # If no additional conditions are provided, add user_sk condition
    scan_params = {
        'FilterExpression': filter_expression
    }
    
    # Perform the scan operation
    response = table.scan(**scan_params)
    
    # Process the response
    items = response.get('Items', [])
    
    
    # Custom encoder for Decimal objects
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

def user_update_handler(event):
    # Extract values from the event, using None as a default if the key is not found
    event = json.loads(event.get('body', '{}'))
    # sk_user_id = event.get('user_id')
    pk_user_id = event.get('pk_user_id')
    sk_id = event.get('sk_id')
    # return user_id
    
    if not pk_user_id :
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'statusCode': "400",
                "body":{
                'message': 'user_id and parent_id are required'
                }
               
            }),
            "isBase64Encoded": False
        }
    
    # Get the current timestamp
    updated_at = datetime.utcnow().isoformat()

    # Extract other attributes to be updated
    update_expression = ['#updated_at = :updated_at']
    expression_attribute_values = {':updated_at': updated_at}
    expression_attribute_names = {'#updated_at': 'updated_at'}

    # if 'profile_img' in event:
    #     update_expression.append('#profile_img = :profile_img')
    #     expression_attribute_values[':profile_img'] = event['profile_img']
    #     expression_attribute_names['#profile_img'] = 'profile_img'
    # if 'location' in event:
    #     update_expression.append('#location = :location')
    #     expression_attribute_values[':location'] = event['location']
    #     expression_attribute_names['#location'] = 'location'
    # if 'phone' in event:
    #     update_expression.append('#phone = :phone')
    #     expression_attribute_values[':phone'] = event['phone']
    #     expression_attribute_names['#phone'] = 'phone'
    if 'user_name' in event:
        update_expression.append('#user_name = :user_name')
        expression_attribute_values[':user_name'] = event['user_name']
        expression_attribute_names['#user_name'] = 'user_name'


    if update_expression:
        update_expression = 'SET ' + ', '.join(update_expression)
        response = table.update_item(
            Key={
                'pk_user_id': pk_user_id
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ExpressionAttributeNames=expression_attribute_names,
            ReturnValues="UPDATED_NEW"
        )
    else:
        return {
            'statusCode': 200,
             'body': json.dumps({
                 'statusCode': "400",
             'body': 'No attributes to update'
             })
         
        }

    # Return a successful response
    return {
        'statusCode': 200,
        'body':json.dumps({
            'statusCode': "200",
        'body': 'Successfully updated data'
        })
        # ,
        # 'updatedAttributes': response['Attributes']
    }
