import json
import boto3

# Initialize the DynamoDB client
dynamodb = boto3.client('dynamodb')

# Table name
TABLE_NAME = 'pet_variety_data'

def fetch_data_from_dynamodb(attribute_prefix=None):
    try:
        # Query the DynamoDB table to get the item with pk_admin_id = '1'
        response = dynamodb.get_item(
            TableName=TABLE_NAME,
            Key={
                'pk_admin_id': {'S': '1'}
            }
        )
        
        # Check if the item exists
        if 'Item' not in response:
            return {
                "statusCode": 200,
                "body": json.dumps({
                    'statusCode': '404',
                    "message": "Item not found"
                })
            }
        
        # Get the item from the response
        item = response['Item']
        result_data = {}
        
        # If an attribute prefix is provided, filter based on that prefix
        for key, value in item.items():
            if attribute_prefix is None or key.startswith(attribute_prefix):
                if 'M' in value:
                    # Extract the values from the map
                    result_data[key] = {k: v['S'] for k, v in value['M'].items()}
                else:
                    result_data[key] = value['S']
        
        # Always include 'disease_result' and 'pedigree_grp'
        if 'disease_result' in item:
            result_data['disease_result'] = {k: v['S'] for k, v in item['disease_result']['M'].items()}
        if 'pedigree_grp' in item:
            result_data['pedigree_grp'] = {k: v['S'] for k, v in item['pedigree_grp']['M'].items()}
        
        # Return the filtered or full attribute values
        return {
            "statusCode": 200,
            "body": json.dumps({
                'statusCode': '200',
                "data": result_data
            })
        }
        
    except Exception as e:
        print(f"Exception in handler: {str(e)}")
        return {
            "statusCode": 200,
            "body": json.dumps({
                'statusCode': '500',
                "message": f"Internal server error: {str(e)}"
            })
        }

def pet_varient_data_handler(event):
    # Ensure event is not None and has the expected structure
    query_params = event.get('queryStringParameters') if event else None
    attribute_type = query_params.get('type') if query_params else None
    
    # Fetch data based on the attribute type or fetch all data if no type is specified
    if attribute_type and attribute_type not in ['cat', 'dog']:
        return {
            "statusCode": 200,
            "body": json.dumps({
                'statusCode': '400',
                "message": "Query parameter 'type' must be either 'cat' or 'dog'"
            })
        }
    
    # If no type is provided, fetch all data from the item
    return fetch_data_from_dynamodb(attribute_type)

