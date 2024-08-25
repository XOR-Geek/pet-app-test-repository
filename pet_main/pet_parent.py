import json
import boto3
import time
import random
from datetime import datetime
from common import CommonConfig
from boto3.dynamodb.conditions import Attr
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
parent_table = dynamodb.Table(CommonConfig.pet_parent_tablename)
child_table = dynamodb.Table(CommonConfig.pet_child_tablename)

def generate_parent_key(sort_key):
    if sort_key is None:
        raise ValueError("sort_key is None")
    last_four = sort_key[-4:]
    unix_timestamp = int(time.time())
    new_sort_key = f"{last_four}{unix_timestamp}"
    return new_sort_key

def generate_random_microchip_no():
    return ''.join([str(random.randint(0, 9)) for _ in range(8)])

def generate_management_number(item_count):
    new_item_number = item_count + 1
    management_number = f"{new_item_number:05d}"
    return management_number

def response_generator(message, statusCode):
    return {
        'statusCode': statusCode,
        'body': message
    }

def parent_add_handler(event):
    event = json.loads(event.get('body', '{}'))
    sort_key = event.get('user_id')
    shop_id = event.get('shop_id')
    birth_date = event.get('birth_date')
    gender = event.get('gender')
    microchip_no = event.get('microchip_no')
    pedigree_grp = event.get('pedigree_grp')
    pet_desc = event.get('pet_desc')
    parent_delete_flag = event.get('pet_flag')
    pet_name = event.get('pet_name')
    pet_weight = event.get('pet_weight')
    pet_status = event.get('pet_status')
    pet_type = event.get('pet_type')
    pet_variety = event.get('pet_variety')
    images = event.get('images')
    coat_color = event.get('coat_color')
    hair_type = event.get('hair_type')
    pedigree_number = event.get('pedigree_number')
    genetic_disease = event.get('genetic_disease')
    created_at = datetime.utcnow().isoformat()
    updated_at = datetime.utcnow().isoformat()

    retire_information = ""

    if sort_key is None:
        return {
            'statusCode': 200,
            'body': json.dumps(response_generator("user_id is required", "400"))
        }

    try:
        partition_key = generate_parent_key(sort_key)
    except ValueError as e:
        return {
            'statusCode': 200,
            'body': str(e)
        }

    response = parent_table.scan()
    # item_count = response.get('Count', 0)
    items = response.get('Items', [])

    management_numbers = [int(item['management_number']) for item in items if 'management_number' in item]

    # Find the maximum management number
    max_management_number = max(management_numbers) if management_numbers else 0

    management_number = generate_management_number(max_management_number)

    item = {
        'pk_parent_id': partition_key,
        'sk_user_id': sort_key,
        'microchip_no': microchip_no,
        'created_at': created_at,
        'pet_weight': pet_weight,
        'updated_at': updated_at,
        'images': images,
        'shop_id': shop_id,
        'birth_date': birth_date,
        'gender': gender,
        'pedigree_grp': pedigree_grp,
        'pet_desc': pet_desc,
        'pet_name': pet_name,
        'pet_status': pet_status,
        'pet_type': pet_type,
        'pet_variety': pet_variety,
        'coat_color': coat_color,
        'hair_type': hair_type,
        'pedigree_number': pedigree_number,
        'genetic_disease': genetic_disease,
        'management_number': management_number,
        'parent_delete_flag': parent_delete_flag,
        "retire_information": retire_information
    }

    response = parent_table.put_item(Item=item)

    return {
        "statusCode": 200,
        "body": json.dumps(response_generator("successfully added data", "200"))
    }

def pet_parent_list_handler(event):
    query_params = event.get('queryStringParameters', {})
    user_id = query_params.get('user_id')
    gender = query_params.get('gender')
    pet_type = query_params.get('pet_type')
    pet_variety = query_params.get('pet_variety')
    pet_status = query_params.get('pet_status')

    if not user_id:
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'statusCode': "400",
                'message': 'user_id is required'
            }),
            "isBase64Encoded": False
        }

    filter_expression = Attr('sk_user_id').eq(user_id)

    if gender is not None:
        filter_expression = filter_expression & Attr('gender').eq(gender)
    if pet_type is not None:
        filter_expression = filter_expression & Attr('pet_type').eq(pet_type)
    if pet_variety is not None:
        filter_expression = filter_expression & Attr('pet_variety').eq(pet_variety)
    if pet_status is not None:
        filter_expression = filter_expression & Attr('pet_status').eq(pet_status)
    filter_expression = filter_expression & Attr('parent_delete_flag').eq("0")

    scan_params = {
        'FilterExpression': filter_expression
    }

    try:
        response = parent_table.scan(**scan_params)
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'statusCode': "500",
                'message': str(e)
            }),
            "isBase64Encoded": False
        }

    items = response.get('Items', [])

    # Sort items by 'management_number' timestamp
    items.sort(key=lambda x: x.get('management_number', ''), reverse=True)

    parent_ids = {item['pk_parent_id']: item['gender'] for item in items}

    children_counts = get_children_count(parent_ids)

    for item in items:
        item['children_count'] = children_counts.get(item['pk_parent_id'], "0")

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

def get_children_count(parent_ids):
    counts = {parent_id: "0" for parent_id in parent_ids}

    for parent_id, gender in parent_ids.items():
        parent_attribute = 'mother_id' if gender == '0' else 'father_id'
        
        try:
            response = child_table.scan(
                FilterExpression=Attr(parent_attribute).eq(parent_id)
            )
            counts[parent_id] = str(response.get('Count', 0))
        except Exception as e:
            counts[parent_id] = "0"
    
    return counts

def pet_parent_details_handler(event):
    table = dynamodb.Table(CommonConfig.pet_parent_tablename)

    query_params = event.get('queryStringParameters', {})
    user_id = query_params.get('user_id')
    parent_id = query_params.get('parent_id')
    parent_delete_flag = query_params.get('parent_delete_flag')

    if not user_id :
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'statusCode': "400",
                    'message': 'user_id is required'
                }),
                "isBase64Encoded": False
            }
    
    if  user_id and parent_delete_flag:
        filter_expression = Attr('sk_user_id').eq(user_id) & Attr('parent_delete_flag').eq(parent_delete_flag)
        scan_params = {'FilterExpression': filter_expression}

        response = table.scan(**scan_params)
        items = response.get('Items', [])

        if not items:
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'statusCode': "404",
                    'message': 'No draft found'
                }),
                "isBase64Encoded": False
            }

        parent_attribute = 'mother_id' if items[0].get('gender') == '0' else 'father_id'

        child_info = get_child_info(user_id, parent_id, parent_attribute)
        response_body = items[0]
        response_body['children_info'] = child_info

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'statusCode': "200",
                'body': response_body
            }, default=decimal_default),
            "isBase64Encoded": False
        }
    if not user_id or not parent_id:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'statusCode': "400",
                'message': 'user_id and parent_id are required'
            }),
            "isBase64Encoded": False
        }

    filter_expression = Attr('sk_user_id').eq(user_id) & Attr('pk_parent_id').eq(parent_id)
    scan_params = {'FilterExpression': filter_expression}

    response = table.scan(**scan_params)
    items = response.get('Items', [])

    if not items:
        return {
            'statusCode': 404,
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

    parent_attribute = 'mother_id' if items[0].get('gender') == '0' else 'father_id'

    child_info = get_child_info(user_id, parent_id, parent_attribute)
    response_body = items[0]
    response_body['children_info'] = child_info
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'statusCode': "200",
            'body': response_body
        }, default=decimal_default),
        "isBase64Encoded": False
    }

def get_child_info(user_id, parent_id, parent_attribute):
    table = dynamodb.Table(CommonConfig.pet_child_tablename)
    try:
        response = table.scan(
            FilterExpression=Attr('sk_user_id').eq(user_id)
        )
        items = response.get('Items', [])
        filtered_items = [item for item in items if item.get(parent_attribute) == parent_id]

        result = {
            "parent_attribute" : parent_attribute,
            "parent_id" : parent_id,
            'total_birth': f"{len(filtered_items)}",
            'children': [
                {
                    'pk_child_id': item['pk_child_id'],
                    'date_of_birth': item['birth_date'],
                    'child_name': item['child_name'],
                    "birth_id": item["birth_id"],
                    'growth_status': "記録中" if item["birth_id"] == "記録中" else "記録済"
                }
                for item in filtered_items
            ]
        }
        return result

    except Exception as e:
        return {
            'total_birth': 0,
            'children': []
        }

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def pet_parent_update_handler(event):
    event = json.loads(event.get('body', '{}'))
    user_id = event.get('user_id')
    parent_id = event.get('parent_id')

    if not user_id or not parent_id:
        return {
            'statusCode': 200,
            'body': json.dumps(response_generator("user_id & parent_id are required", "400"))
        }

    updated_at = datetime.utcnow().isoformat()

    update_expression = ['#updated_at = :updated_at']
    expression_attribute_values = {':updated_at': updated_at}
    expression_attribute_names = {'#updated_at': 'updated_at'}

    if 'shop_id' in event:
        update_expression.append('#shop_id = :shop_id')
        expression_attribute_values[':shop_id'] = event['shop_id']
        expression_attribute_names['#shop_id'] = 'shop_id'
    if 'birth_date' in event:
        update_expression.append('#birth_date = :birth_date')
        expression_attribute_values[':birth_date'] = event['birth_date']
        expression_attribute_names['#birth_date'] = 'birth_date'
    if 'gender' in event:
        update_expression.append('#gender = :gender')
        expression_attribute_values[':gender'] = event['gender']
        expression_attribute_names['#gender'] = 'gender'
    if 'pedigree_grp' in event:
        update_expression.append('#pedigree_grp = :pedigree_grp')
        expression_attribute_values[':pedigree_grp'] = event['pedigree_grp']
        expression_attribute_names['#pedigree_grp'] = 'pedigree_grp'
    if 'pet_desc' in event:
        update_expression.append('#pet_desc = :pet_desc')
        expression_attribute_values[':pet_desc'] = event['pet_desc']
        expression_attribute_names['#pet_desc'] = 'pet_desc'
    if 'parent_delete_flag' in event:
        update_expression.append('#parent_delete_flag = :parent_delete_flag')
        expression_attribute_values[':parent_delete_flag'] = event['parent_delete_flag']
        expression_attribute_names['#parent_delete_flag'] = 'parent_delete_flag'
    if 'pet_name' in event:
        update_expression.append('#pet_name = :pet_name')
        expression_attribute_values[':pet_name'] = event['pet_name']
        expression_attribute_names['#pet_name'] = 'pet_name'
    if 'pet_status' in event:
        update_expression.append('#pet_status = :pet_status')
        expression_attribute_values[':pet_status'] = event['pet_status']
        expression_attribute_names['#pet_status'] = 'pet_status'
    if 'pet_type' in event:
        update_expression.append('#pet_type = :pet_type')
        expression_attribute_values[':pet_type'] = event['pet_type']
        expression_attribute_names['#pet_type'] = 'pet_type'
    if 'pet_variety' in event:
        update_expression.append('#pet_variety = :pet_variety')
        expression_attribute_values[':pet_variety'] = event['pet_variety']
        expression_attribute_names['#pet_variety'] = 'pet_variety'
    if 'pet_weight' in event:
        update_expression.append('#pet_weight = :pet_weight')
        expression_attribute_values[':pet_weight'] = event['pet_weight']
        expression_attribute_names['#pet_weight'] = 'pet_weight'
    if 'images' in event:
        update_expression.append('#images = :images')
        expression_attribute_values[':images'] = event['images']
        expression_attribute_names['#images'] = 'images'
    if 'coat_color' in event:
        update_expression.append('#coat_color = :coat_color')
        expression_attribute_values[':coat_color'] = event['coat_color']
        expression_attribute_names['#coat_color'] = 'coat_color'
    if 'hair_type' in event:
        update_expression.append('#hair_type = :hair_type')
        expression_attribute_values[':hair_type'] = event['hair_type']
        expression_attribute_names['#hair_type'] = 'hair_type'
    if 'parent_delete_flag' in event:
        update_expression.append('#parent_delete_flag = :parent_delete_flag')
        expression_attribute_values[':parent_delete_flag'] = event['parent_delete_flag']
        expression_attribute_names['#parent_delete_flag'] = 'parent_delete_flag'
    if 'pedigree_number' in event:
        update_expression.append('#pedigree_number = :pedigree_number')
        expression_attribute_values[':pedigree_number'] = event['pedigree_number']
        expression_attribute_names['#pedigree_number'] = 'pedigree_number'
    if 'genetic_disease' in event:
        update_expression.append('#genetic_disease = :genetic_disease')
        expression_attribute_values[':genetic_disease'] = event['genetic_disease']
        expression_attribute_names['#genetic_disease'] = 'genetic_disease'
    if 'microchip_no' in event:
        update_expression.append('#microchip_no = :microchip_no')
        expression_attribute_values[':microchip_no'] = event['microchip_no']
        expression_attribute_names['#microchip_no'] = 'microchip_no'
    if 'retire_information' in event:
        update_expression.append('#retire_information = :retire_information')
        expression_attribute_values[':retire_information'] = event['retire_information']
        expression_attribute_names['#retire_information'] = 'retire_information'

    update_expression = 'SET ' + ', '.join(update_expression)

    try:
        response = parent_table.update_item(
            Key={
                'pk_parent_id': parent_id,
                'sk_user_id': user_id
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ExpressionAttributeNames=expression_attribute_names,
            ReturnValues="UPDATED_NEW"
        )
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(response_generator(str(e), "500"))
        }

    return {
        'statusCode': 200,
        'body': json.dumps(response_generator("successfully updated data", "200"))
    }

def admin_parent_list_handler(event):
    try:
        dynamodb = boto3.resource('dynamodb')
        print("Initialized DynamoDB resource.")
        
        table = dynamodb.Table('pet_parent_dev')
        print("Selected DynamoDB table: pet_parent_dev")
        
        try:
            response = table.scan()
            print("Scan operation successful.")
        except Exception as e:
            print(f"Exception during DynamoDB scan: {str(e)}")
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'statusCode': '500',
                    'message': 'Error scanning DynamoDB table'
                }),
                "isBase64Encoded": False
            }
        
        items = response.get('Items', [])
        print("Items retrieved:", items)

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
                'statusCode': '200',
                'body': items
            }, default=decimal_default),
            "isBase64Encoded": False
        }

    except Exception as e:
        print(f"Unexpected exception: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'statusCode': '500',
                'message': 'Internal server error in parent_list_handler'
            }),
            "isBase64Encoded": False
        }
