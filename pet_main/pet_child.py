import json
import boto3
from boto3.dynamodb.conditions import Attr
from common import CommonConfig
from decimal import Decimal
import time
import random
from datetime import datetime

dynamodb = boto3.resource('dynamodb')

# Select your DynamoDB tables
table = dynamodb.Table(CommonConfig.pet_child_tablename)
outside_father_table = dynamodb.Table(CommonConfig.pet_outside_father_tablename)

def pet_child_details_handler(event):
    query_params = event.get('queryStringParameters', {})
    user_id = query_params.get('user_id')
    child_id = query_params.get('child_id')

    if not user_id or not child_id:
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'statusCode': "400",
                'message': 'user_id and child_id are required'
            }),
            "isBase64Encoded": False
        }

    filter_expression = Attr('sk_user_id').eq(user_id) & Attr('pk_child_id').eq(child_id)
    scan_params = {'FilterExpression': filter_expression}

    # Perform the scan operation
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
                'message': 'No items found'
            }),
            "isBase64Encoded": False
        }

    # Retrieve the mother and father IDs
    mother_id = items[0]['mother_id']
    father_id = items[0]['father_id']

    # Get parent details and number of children
    parent_table = dynamodb.Table(CommonConfig.pet_parent_tablename)

    # Retrieve mother details
    mother_expression = Attr('pk_parent_id').eq(mother_id)
    mother_params = {'FilterExpression': mother_expression}
    mother_response = parent_table.scan(**mother_params)
    mother_info = mother_response.get('Items', [])

    # Retrieve father details
    if items[0]['father_status'] == '0':
        father_expression = Attr('pk_parent_id').eq(father_id)
        father_params = {'FilterExpression': father_expression}
        
        # Perform the scan operation
        father_response = parent_table.scan(**father_params)
        father_info = father_response.get('Items', [])
    else:
        outside_father_table = dynamodb.Table(CommonConfig.pet_outside_father_tablename)
        outside_father_expression = Attr('pk_outside_father_id').eq(father_id)
        outside_father_params = {'FilterExpression': outside_father_expression}
        
        # Perform the scan operation
        outside_father_response = outside_father_table.scan(**outside_father_params)
        father_info = outside_father_response.get('Items', [])

    # Get the number of children for the mother and father
    mother_child_count = get_child_info(user_id, mother_id, 'mother_id')
    father_child_count = get_child_info(user_id, father_id, 'father_id')

    # Add the count of children to the parent details
    if mother_info:
        mother_info[0]['number_of_child'] = str(mother_child_count['total_birth'])
    if father_info:
        father_info[0]['number_of_child'] = str(father_child_count['total_birth'])

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
            'body': {
                'child': items[0],
                'mother': mother_info[0] if mother_info else {},
                'father': father_info[0] if father_info else {}
            }
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
            # "parent_attribute": parent_attribute,
            # "parent_id": parent_id,
            'total_birth': len(filtered_items),
            # 'children': [
            #     {
            #         'pk_child_id': item['pk_child_id'],
            #         'date_of_birth': item['birth_date'],
            #         'child_name': item['child_name'],
            #         'growth_status': "recording" if item["birth_id"] != "Not issued yet" else "record_complete"
            #     }
            #     for item in filtered_items
            # ]
        }
        return result

    except Exception as e:
        return {
            'total_birth': 0,
            'children': []
        }

def pet_child_list_handler(event):
    query_params = event.get('queryStringParameters', {})
    user_id = query_params.get('user_id')
    gender = query_params.get('gender')
    child_type = query_params.get('child_type')
    child_variety = query_params.get('child_variety')
    child_status = query_params.get('child_status')

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
    
    if child_type is not None:
        filter_expression = filter_expression & Attr('child_type').eq(child_type)
    
    if child_variety is not None:
        filter_expression = filter_expression & Attr('child_variety').eq(child_variety)
    
    if child_status is not None:
        filter_expression = filter_expression & Attr('child_status').eq(child_status)

    ##deleted items hide
    filter_expression = filter_expression & Attr('child_delete_flag').eq("0")
    
    scan_params = {
        'FilterExpression': filter_expression
    }

    # Perform the scan operation
    response = table.scan(**scan_params)

    # Process the response
    items = response.get('Items', [])

    # Sort items by 'management_number' timestamp
    items.sort(key=lambda x: x.get('child_management_id', ''), reverse=True)

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

def generate_parent_key(sort_key):
    last_four = sort_key[-4:]
    unix_timestamp = int(time.time())
    sort_key = f"{last_four}{unix_timestamp}"
    return sort_key

def generate_random_microchip_no():
    return ''.join([str(random.randint(0, 9)) for _ in range(8)])

def generate_child_management_id(item_count):
    # Increment the item count to get the new item's management number
    new_item_number = item_count + 1
    # Format the new item number as a zero-padded string of length 5
    management_number = f"{new_item_number:05d}"
    return management_number

def pet_child_add_handler(event):
    event = json.loads(event.get('body', '{}'))
    sort_key = event.get('sk_user_id')
    shop_id = event.get('shop_id')
    birth_date = event.get('birth_date')
    gender = event.get('gender')
    birth_id = "Not issued yet"
    child_delete_flag = "0"
    child_name = event.get('child_name')
    child_weight = event.get('child_weight')
    child_status = event.get('child_status')
    child_type = event.get('child_type')
    child_variety = event.get('child_variety')
    images = event.get('images')
    day15 = event.get('day15')
    day30 = event.get('day30')
    day45 = event.get('day45')
    mother_id = event.get('mother_id')
    father_id = event.get('father_id')
    father_status = event.get('father_status')
    number_of_birth = event.get('number_of_birth')
    number_of_stillbirth = event.get('number_of_stillbirth')
    gender_male = event.get('gender_male')
    gender_female = event.get('gender_female')
    created_at = datetime.utcnow().isoformat()
    updated_at = datetime.utcnow().isoformat()

    # Scan the table to count existing items
    response = table.scan()
    # item_count = response.get('Count', 0)
    items = response.get('Items', [])

    management_numbers = [int(item['child_management_id']) for item in items if 'child_management_id' in item]

    # Find the maximum management number
    max_management_number = max(management_numbers) if management_numbers else 0

    # Generate the child management number
    child_management_id = generate_child_management_id(max_management_number)

    partition_key = generate_parent_key(sort_key)
    item = {
        'pk_child_id': partition_key,
        'sk_user_id': sort_key,
        'birth_id': birth_id,
        'created_at': created_at,
        'updated_at': updated_at,
        'child_weight': child_weight,
        'images': images,
        'shop_id': shop_id,
        'birth_date': birth_date,
        'gender': gender,
        'child_delete_flag': child_delete_flag,
        'child_name': child_name,
        'child_status': child_status,
        'child_type': child_type,
        'child_variety': child_variety,
        'day0': {'weight': child_weight, 'image': ''},
        'day15': day15,
        'day30': day30,
        'day45': day45,
        'mother_id': mother_id,
        'father_id': father_id,
        'father_status': father_status,
        'number_of_birth': number_of_birth,
        'number_of_stillbirth': number_of_stillbirth,
        'gender_male': gender_male,
        'gender_female': gender_female,
        'child_management_id': child_management_id
    }

    response = table.put_item(Item=item)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'statusCode': "200",
            'message': 'Successfully added data'
        })
    }

def pet_child_day_update_handler(event):
    event = json.loads(event.get('body', '{}'))
    user_id = event.get('user_id')
    child_id = event.get('child_id')

    if not user_id or not child_id:
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'statusCode': "400",
                'message': 'user_id and child_id are required'
            }),
            "isBase64Encoded": False
        }

    updated_at = datetime.utcnow().isoformat()
    update_expression = ['#updated_at = :updated_at']
    expression_attribute_values = {':updated_at': updated_at}
    expression_attribute_names = {'#updated_at': 'updated_at'}

    if 'day15' in event:
        update_expression.append('#day15 = :day15')
        expression_attribute_values[':day15'] = event['day15']
        expression_attribute_names['#day15'] = 'day15'
        
    if 'day30' in event:
        update_expression.append('#day30 = :day30')
        expression_attribute_values[':day30'] = event['day30']
        expression_attribute_names['#day30'] = 'day30'
        
    if 'day45' in event:
        update_expression.append('#day45 = :day45')
        expression_attribute_values[':day45'] = event['day45']
        expression_attribute_names['#day45'] = 'day45'

    if update_expression:
        update_expression = 'SET ' + ', '.join(update_expression)
        response = table.update_item(
            Key={
                'pk_child_id': child_id,
                'sk_user_id': user_id,
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
                'message':  'No attributes to update'
            })
        }

    return {
        'statusCode': 200,
        'body': json.dumps({
            'statusCode': "200",
            'message':  'Successfully updated data',
        })
    }

def outside_father_entry_handler(event):
    event = json.loads(event.get('body', '{}'))
    sort_key = event.get('sk_user_id')
    shop_id = event.get('shop_id')
    birth_date = event.get('birth_date')
    gender = event.get('gender')
    # management_number = event.get('management_number')
    microchip_no = event.get('microcheap_no')
    pedigree_grp = event.get('pedigree_grp')
    pet_desc = event.get('pet_desc')
    pet_name = event.get('pet_name')
    pet_weight = event.get('pet_weight')
    pet_status = event.get('pet_status')
    pet_type = event.get('pet_type')
    pet_variety = event.get('pet_variety')
    images = event.get('images')
    created_at = datetime.utcnow().isoformat()
    updated_at = datetime.utcnow().isoformat()
    coat_color = event.get('coat_color')
    hair_type = event.get('hair_type')
    pedigree_number = event.get('pedigree_number')
    genetic_disease = event.get('genetic_disease')

    #bydefault values:
    parent_delete_flag = "0"
    retire_information = {
        "information": {"S": ""},
        "reason": {"S": "0"},
        "retire_date": {"S": ""}
    }

    # Scan the table to count existing items
    response = outside_father_table.scan()
    item_count = response.get('Count', 0)

    # Generate the management number
    management_number = generate_management_number(item_count)

    partition_key = generate_parent_key(sort_key)
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
        'retire_information': retire_information
    }
    # print(images)
    # item['images'] = images
    # if shop_id is not None:
    #     item['shop_id'] = shop_id
    # if birth_date is not None:
    #     item['birth_date'] = birth_date
    # if gender is not None:
    #     item['gender'] = gender
    # if management_number is not None:
    #     item['management_number'] = management_number
    # if pedigree_grp is not None:
    #     item['pedigree_grp'] = pedigree_grp
    # if pet_desc is not None:
    #     item['pet_desc'] = pet_desc
    # if coat_color is not None:
    #     item['coat_color'] = coat_color
    # if hair_type is not None:
    #     item['hair_type'] = hair_type
    # if pedigree_number is not None:
    #     item['pedigree_number'] = pedigree_number
    # if genetic_diseases is not None:
    #     item['genetic_diseases'] = genetic_diseases 
    # if pet_name is not None:
    #     item['pet_name'] = pet_name
    # if pet_status is not None:
    #     item['pet_status'] = pet_status
    # if pet_type is not None:
    #     item['pet_type'] = pet_type
    # if pet_variety is not None:
    #     item['pet_variety'] = pet_variety      

    response = outside_father_table.put_item(Item=item)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'statusCode': "200",
            'message': 'Successfully added data'
        })
    }

def outside_father_update_handler(event):
    event = json.loads(event.get('body', '{}'))
    user_id = event.get('user_id')
    outside_father_id = event.get('outside_father_id')

    if not user_id or not outside_father_id:
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'statusCode': "400",
                'message': 'user_id and outside_father_id are required',
                'user_id': user_id,
                'outside_father_id': outside_father_id
            }),
            "isBase64Encoded": False
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
        update_expression.append('#pet_flag = :pet_flag')
        expression_attribute_values[':pet_flag'] = event['pet_flag']
        expression_attribute_names['#pet_flag'] = 'pet_flag'
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
    if 'microcheap_no' in event:
        update_expression.append('#microcheap_no = :microcheap_no')
        expression_attribute_values[':microcheap_no'] = event['microcheap_no']
        expression_attribute_names['#microcheap_no'] = 'microcheap_no'
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
    if 'pedigree_number' in event:
        update_expression.append('#pedigree_number = :pedigree_number')
        expression_attribute_values[':pedigree_number'] = event['pedigree_number']
        expression_attribute_names['#pedigree_number'] = 'pedigree_number'
    if 'genetic_diseases' in event:
        update_expression.append('#genetic_diseases = :genetic_diseases')
        expression_attribute_values[':genetic_diseases'] = event['genetic_diseases']
        expression_attribute_names['#genetic_diseases'] = 'genetic_diseases'
    if 'retire_information' in event:
        update_expression.append('#retire_information = :retire_information')
        expression_attribute_values[':retire_information'] = event['retire_information']
        expression_attribute_names['#retire_information'] = 'retire_information'

    if update_expression:
        update_expression = 'SET ' + ', '.join(update_expression)
        response = outside_father_table.update_item(
            Key={
                'pk_outside_father_id': outside_father_id,
                'sk_user_id': user_id,
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
                'message':  'No attributes to update'
            })
        }

    return {
        'statusCode': 200,
        'body': json.dumps({
            'statusCode': "200",
            'message':  'Successfully updated data'
        })
    }

def outside_father_details_handler(event):
    query_params = event.get('queryStringParameters', {})
    user_id = query_params.get('user_id')
    parent_id = query_params.get('outside_father_id')

    if not user_id or not parent_id:
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'statusCode': "400",
                'message': 'user_id and outside_father_id are required'
            }),
            "isBase64Encoded": False
        }
    filter_expression = Attr('sk_user_id').eq(user_id) & Attr('pk_outside_father_id').eq(parent_id)

    scan_params = {
        'FilterExpression': filter_expression
    }

    # Perform the scan operation
    response = outside_father_table.scan(**scan_params)

    # Process the response
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

def admin_child_list_handler(event):
    print("Received event in child_list_handler:", json.dumps(event, indent=2))

    try:
        # Initialize a session using Amazon DynamoDB
        dynamodb = boto3.resource('dynamodb')
        print("Initialized DynamoDB resource.")
        
        # Select your DynamoDB table
        table = dynamodb.Table('pet_child_dev')
        print("Selected DynamoDB table: pet_child_dev")
        
        # Perform the scan operation
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
        
        # Process the response
        items = response.get('Items', [])
        print("Items retrieved:", items)
        
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
                'message': 'Internal server error in child_list_handler'
            }),
            "isBase64Encoded": False
        }
