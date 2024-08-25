import json
import boto3
from common import CommonConfig

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb')

# Table name
TABLE_NAME = CommonConfig.pet_child_tablename
def parent_children_handler(event):
    # Extract query parameters
    params = event.get('queryStringParameters', {})
    if not params or 'user_id' not in params or 'parent_id' not in params or 'type' not in params:
        return {
            "statusCode": 400,
            "body": json.dumps({
                'statusCode': '400',
                "message": "Query parameters 'user_id', 'parent_id', and 'type' are required"
            })
        }

    user_id = params['user_id']
    parent_id = params['parent_id']
    parent_type = params['type']

    # Validate type
    if parent_type not in ['0', '1']:
        return {
            "statusCode": 400,
            "body": json.dumps({
                'statusCode': '400',
                "message": "Query parameter 'type' must be '0' (mother) or '1' (father)"
            })
        }

    parent_attribute = 'mother_id' if parent_type == '1' else 'father_id'

    try:
        # Query the DynamoDB table to get the items with sk_user_id = user_id
        table = dynamodb.Table(TABLE_NAME)
        response = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('sk_user_id').eq(user_id)
        )
        
        # Check if items exist
        if 'Items' not in response or not response['Items']:
            return {
                "statusCode": 404,
                "body": json.dumps({
                    'statusCode': '404',
                    "message": "No items found for the provided user_id"
                })
            }
        
        items = response['Items']
        filtered_items = [item for item in items if item.get(parent_attribute) == parent_id]

        # Prepare the response
        result = {
            'total_birth': len(filtered_items),
            'children': [
                {
                    'pk_child_id': item['pk_child_id'],
                    'date_of_birth': item['birth_date'],
                    'father_id': item['father_id']
                }
                for item in filtered_items
            ]
        }
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                'statusCode': '200',
                'result': result
            })
        }
        
    except Exception as e:
        print(f"Exception in handler for parent_children: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                'statusCode': '500',
                "message": f"Internal server error: {str(e)}"
            })
        }



# from parent_children import parent_children_handler

#         elif resource == "/parent_children":
#             response = parent_children_handler(event)