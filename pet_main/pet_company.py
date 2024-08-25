import json
import time
import boto3
from datetime import datetime
from boto3.dynamodb.conditions import Attr
from decimal import Decimal
from common import CommonConfig

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(CommonConfig.pet_company_tablename)

# Function to generate response
def response_generator(message, statusCode):
    return {
        'statusCode': statusCode,
        'body': message
    }

# Function to generate parent key
def generate_parent_key(sort_key):
    if sort_key is None:
        raise ValueError("sort_key is None")
    # Extract the last 4 characters from the sort_key
    last_four = sort_key[-4:]
    # Get the current Unix timestamp
    unix_timestamp = int(time.time())
    # Concatenate the last four digits of the sort_key and the Unix timestamp
    new_sort_key = f"{last_four}{unix_timestamp}"
    return new_sort_key

def company_details_handler(event):

    
    # Extract query parameters safely
    query_params = event.get('queryStringParameters', {})
    company_id = query_params.get('pk_company_id')    
    if not company_id:
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'statusCode': "400",
                'message': 'company_id is required'
            }),
            "isBase64Encoded": False
        }
    
    # Start building the filter expression with user_id
    filter_expression = Attr('pk_company_id').eq(company_id)
    
    # Add additional conditions if they are not None
    conditions_present = False
    
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


def admin_company_list_handler(event):
    print("Received event in company_list_handler:", json.dumps(event, indent=2))

    try:
        # Initialize a session using Amazon DynamoDB
        dynamodb = boto3.resource('dynamodb')
        print("Initialized DynamoDB resource.")
        
        # Select your DynamoDB table
        table = dynamodb.Table('pet_company_dev')
        print("Selected DynamoDB table: pet_company_dev")
        
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
                'message': 'Internal server error in company_list_handler'
            }),
            "isBase64Encoded": False
        }


def admin_edit_log_handler(event):
    print("Received event in edit_log_list_handler:", json.dumps(event, indent=2))

    try:
        # Initialize a session using Amazon DynamoDB
        dynamodb = boto3.resource('dynamodb')
        print("Initialized DynamoDB resource.")
        
        # Select your DynamoDB table
        table = dynamodb.Table('rx_edit_log')
        print("Selected DynamoDB table: rx_edit_log")
        
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
                'message': 'Internal server error in edit_log_list_handler'
            }),
            "isBase64Encoded": False
        }


def admin_member_list_handler(event):
    print("Received event in member_list_handler:", json.dumps(event, indent=2))

    try:
        # Initialize a session using Amazon DynamoDB
        dynamodb = boto3.resource('dynamodb')
        print("Initialized DynamoDB resource.")
        
        # Select your DynamoDB table
        table = dynamodb.Table('pet_user')
        print("Selected DynamoDB table: pet_user")
        
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
                'message': 'Internal server error in member_list_handler'
            }),
            "isBase64Encoded": False
        }
    
# Lambda handler for new company registraton
def admin_company_registration_handler(event):
    print("Received event for new company registration.")

    # get event
    event = json.loads(event.get('body', '{}'))

    # TODO: add check whether company already exists or not

    # get all the properties
    partition_key = event.get("company_id")
    corporate_classification = event.get('corporate_classification')
    name = event.get('name')
    name_furigana = event.get('name_furigana')
    representative_name = event.get('representative_name')
    post_code = event.get('post_code')
    location_prefecture = event.get('location_prefecture')
    location_city = event.get('location_city')
    location_chome = event.get('location_chome')
    telephone_number = event.get('telephone_number')
    mobile_number = event.get('mobile_number')
    fax_number = event.get('fax_number')
    email = event.get('email')
    production_area = event.get('production_area')
    military_name = event.get('military_name')
    breeder_representation = event.get('breeder_representation')
    production_prefecture = event.get('production_prefecture')
    affiliated_park = event.get('affiliated_park')
    number = event.get('number')
    date_expiry = event.get('date_expiry')
    representative_name_furigana = event.get('representative_name_furigana')
    created_at = datetime.utcnow().isoformat()
    updated_at = datetime.utcnow().isoformat()

    # Validate required fields
    if partition_key is None:
        return {
            'statusCode': 200,
            'body': json.dumps(response_generator("company_id is required", "400"))
        }
    
    if name is None:
        return {
            'statusCode': 200,
            'body': json.dumps(response_generator("name is required", "400"))
        }
    
    if representative_name is None:
        return {
            'statusCode': 200,
            'body': json.dumps(response_generator("representative_name is required", "400"))
        }
    
    if email is None:
        return {
            'statusCode': 200,
            'body': json.dumps(response_generator("email is required", "400"))
        }
    
    if affiliated_park is None:
        return {
            'statusCode': 200,
            'body': json.dumps(response_generator("affiliated_park is required", "400"))
        }
    
    # Generate the sort key
    try:
        sort_key = generate_parent_key(partition_key)
    except ValueError as e:
        return {
            'statusCode': 200,
            'body': json.dumps(response_generator(e, "500"))
        }
    
    # Create the item to be added, including only non-None values
    item = {
        'pk_company_id': partition_key,
        'sk_user_id': sort_key,
        'created_at': created_at,
        'updated_at': updated_at,
        'delete_flag': '0',
        'status': '1',
        'email': email, # changed
        'post_code': post_code,
        'location_prefecture': location_prefecture,
        'location_city': location_city,
        'location_chome': location_chome,
        'name': name,
        'name_furigana': name_furigana,
        'telephone_number': telephone_number,
        'mobile_number': mobile_number,
        'fax_number': fax_number,
        'number': number,
        'corporate_classification': corporate_classification,
        'representative_name': representative_name,
        'representative_name_furigana': representative_name_furigana,
        'production_area': production_area,
        'military_name': military_name,
        'breeder_representation': breeder_representation,
        'production_prefecture': production_prefecture,
        'affiliated_park': affiliated_park,
        'date_expiry': date_expiry,
    }

    # add item to dynamodb
    try:
        response = table.put_item(Item=item)
    except Exception as e:
        print("Exception during put item into dynamoDB", e)
        return {
            'statusCode': 500,
            'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
            'body': json.dumps(response_generator(e, "500")),
            "isBase64Encoded": False
        }
    
    return {
        'statusCode': 200,
            'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
            'body': json.dumps(response_generator("Data successfully added", "200")),
            "isBase64Encoded": False
    }

# Lambda handler for company update
def admin_company_update_handler(event):
    print("Received event for existing company update.")

    # get event
    event = json.loads(event.get('body', '{}'))

    # get all the attributes
    company_parent_id = event.get("pk_company_id")
    company_user_id = event.get("sk_user_id")
    corporate_classification = event.get('corporate_classification')
    name = event.get('name')
    name_furigana = event.get('name_furigana')
    representative_name = event.get('representative_name')
    post_code = event.get('post_code')
    location_prefecture = event.get('location_prefecture')
    location_city = event.get('location_city')
    location_chome = event.get('location_chome')
    telephone_number = event.get('telephone_number')
    mobile_number = event.get('mobile_number')
    fax_number = event.get('fax_number')
    email = event.get('email')
    production_area = event.get('production_area')
    military_name = event.get('military_name')
    breeder_representation = event.get('breeder_representation')
    production_prefecture = event.get('production_prefecture')
    affiliated_park = event.get('affiliated_park')
    number = event.get('number')
    date_expiry = event.get('date_expiry')
    representative_name_furigana = event.get('representative_name_furigana')
    received_updated_at = event.get('updated_at')

    # checking whether company exists or not
    if not company_user_id or not company_parent_id:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response_generator("pk_company_id and sk_user_id are required", "400")),
            "isBase64Encoded": False
        }
    items = get_company(company_parent_id, company_user_id)

    if not items:
        return {
            'statusCode': 404,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response_generator("No such company exists.", "404")),
            "isBase64Encoded": False
        }
    
    # compare received and existing updated_at
    if received_updated_at is None:
        return {
            'statusCode': 200,
            'body': json.dumps(response_generator("updated_at is required", "400"))
        }
    
    company_data = items[0]

    old_updated_at = company_data.get('updated_at')

    if not is_date_time_equal(received_updated_at, old_updated_at):
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response_generator("Existing updated_at does not match with the received updated_at.", "500")),
            "isBase64Encoded": False
        }
    
    # Validate required fields
    if corporate_classification is None:
        return {
            'statusCode': 200,
            'body': json.dumps(response_generator("corporate_classification is required", "400"))
        }
    
    if name is None:
        return {
            'statusCode': 200,
            'body': json.dumps(response_generator("name is required", "400"))
        }
    
    if representative_name is None:
        return {
            'statusCode': 200,
            'body': json.dumps(response_generator("representative_name is required", "400"))
        }
    
    if email is None:
        return {
            'statusCode': 200,
            'body': json.dumps(response_generator("email is required", "400"))
        }
    
    if affiliated_park is None:
        return {
            'statusCode': 200,
            'body': json.dumps(response_generator("affiliated_park is required", "400"))
        }
    
    if name_furigana is None:
        return {
            'statusCode': 200,
            'body': json.dumps(response_generator("name_furigana is required", "400"))
        }
    
    if post_code is None:
        return {
            'statusCode': 200,
            'body': json.dumps(response_generator("post_code is required", "400"))
        }
    
    if location_prefecture is None:
        return {
            'statusCode': 200,
            'body': json.dumps(response_generator("location_prefecture is required", "400"))
        }
    
    if location_city is None:
        return {
            'statusCode': 200,
            'body': json.dumps(response_generator("location_city is required", "400"))
        }
    
    if location_chome is None:
        return {
            'statusCode': 200,
            'body': json.dumps(response_generator("location_chome is required", "400"))
        }
    
    if telephone_number is None:
        return {
            'statusCode': 200,
            'body': json.dumps(response_generator("telephone_number is required", "400"))
        }
    
    if mobile_number is None:
        return {
            'statusCode': 200,
            'body': json.dumps(response_generator("mobile_number is required", "400"))
        }
    
    if fax_number is None:
        return {
            'statusCode': 200,
            'body': json.dumps(response_generator("fax_number is required", "400"))
        }
    
    if production_area is None:
        return {
            'statusCode': 200,
            'body': json.dumps(response_generator("production_area is required", "400"))
        }
    
    if military_name is None:
        return {
            'statusCode': 200,
            'body': json.dumps(response_generator("military_name is required", "400"))
        }
    
    if breeder_representation is None:
        return {
            'statusCode': 200,
            'body': json.dumps(response_generator("breeder_representation is required", "400"))
        }
    
    if production_prefecture is None:
        return {
            'statusCode': 200,
            'body': json.dumps(response_generator("production_prefecture is required", "400"))
        }
    
    if number is None:
        return {
            'statusCode': 200,
            'body': json.dumps(response_generator("number is required", "400"))
        }
    
    if date_expiry is None:
        return {
            'statusCode': 200,
            'body': json.dumps(response_generator("date_expiry is required", "400"))
        }
    
    if representative_name_furigana is None:
        return {
            'statusCode': 200,
            'body': json.dumps(response_generator("date_expiry is required", "400"))
        }

    # create update expressions
    # updated_at
    updated_at = datetime.utcnow().isoformat()
    update_expression = ['#updated_at = :updated_at']
    expression_attribute_values = {':updated_at': updated_at}
    expression_attribute_names = {'#updated_at': 'updated_at'}

    # corporate_classification
    update_expression.append('#corporate_classification = :corporate_classification')
    expression_attribute_values[':corporate_classification'] = corporate_classification
    expression_attribute_names['#corporate_classification'] = 'corporate_classification'

    # name
    update_expression.append('#name = :name')
    expression_attribute_values[':name'] = name
    expression_attribute_names['#name'] = 'name'

    # name_furigana
    update_expression.append('#name_furigana = :name_furigana')
    expression_attribute_values[':name_furigana'] = name_furigana
    expression_attribute_names['#name_furigana'] = 'name_furigana'

    # representative_name
    update_expression.append('#representative_name = :representative_name')
    expression_attribute_values[':representative_name'] = representative_name
    expression_attribute_names['#representative_name'] = 'representative_name'

    # post_code
    update_expression.append('#post_code = :post_code')
    expression_attribute_values[':post_code'] = post_code
    expression_attribute_names['#post_code'] = 'post_code'

    # location_prefecture
    update_expression.append('#location_prefecture = :location_prefecture')
    expression_attribute_values[':location_prefecture'] = location_prefecture
    expression_attribute_names['#location_prefecture'] = 'location_prefecture'

    # location_city
    update_expression.append('#location_city = :location_city')
    expression_attribute_values[':location_city'] = location_city
    expression_attribute_names['#location_city'] = 'location_city'

    # location_chome
    update_expression.append('#location_chome = :location_chome')
    expression_attribute_values[':location_chome'] = location_chome
    expression_attribute_names['#location_chome'] = 'location_chome'

    # telephone_number
    update_expression.append('#telephone_number = :telephone_number')
    expression_attribute_values[':telephone_number'] = telephone_number
    expression_attribute_names['#telephone_number'] = 'telephone_number'

    # mobile_number
    update_expression.append('#mobile_number = :mobile_number')
    expression_attribute_values[':mobile_number'] = mobile_number
    expression_attribute_names['#mobile_number'] = 'mobile_number'

    # fax_number
    update_expression.append('#fax_number = :fax_number')
    expression_attribute_values[':fax_number'] = fax_number
    expression_attribute_names['#fax_number'] = 'fax_number'

    # email
    update_expression.append('#email = :email')
    expression_attribute_values[':email'] = email
    expression_attribute_names['#email'] = 'email'

    # production_area
    update_expression.append('#production_area = :production_area')
    expression_attribute_values[':production_area'] = production_area
    expression_attribute_names['#production_area'] = 'production_area'

    # military_name
    update_expression.append('#military_name = :military_name')
    expression_attribute_values[':military_name'] = military_name
    expression_attribute_names['#military_name'] = 'military_name'

    # breeder_representation
    update_expression.append('#breeder_representation = :breeder_representation')
    expression_attribute_values[':breeder_representation'] = breeder_representation
    expression_attribute_names['#breeder_representation'] = 'breeder_representation'

    # production_prefecture
    update_expression.append('#production_prefecture = :production_prefecture')
    expression_attribute_values[':production_prefecture'] = production_prefecture
    expression_attribute_names['#production_prefecture'] = 'production_prefecture'

    # affiliated_park
    update_expression.append('#affiliated_park = :affiliated_park')
    expression_attribute_values[':affiliated_park'] = affiliated_park
    expression_attribute_names['#affiliated_park'] = 'affiliated_park'

    # number
    update_expression.append('#number = :number')
    expression_attribute_values[':number'] = number
    expression_attribute_names['#number'] = 'number'

    # date_expiry
    update_expression.append('#date_expiry = :date_expiry')
    expression_attribute_values[':date_expiry'] = date_expiry
    expression_attribute_names['#date_expiry'] = 'date_expiry'

    # representative_name_furigana
    update_expression.append('#representative_name_furigana = :representative_name_furigana')
    expression_attribute_values[':representative_name_furigana'] = representative_name_furigana
    expression_attribute_names['#representative_name_furigana'] = 'representative_name_furigana'

    # status
    if 'status' in event:
        update_expression.append('#status = :status')
        expression_attribute_values[':status'] = event['status']
        expression_attribute_names['#status'] = 'status'
    
    # delete_flag
    if 'delete_flag' in event:
        update_expression.append('#delete_flag = :delete_flag')
        expression_attribute_values[':delete_flag'] = event['delete_flag']
        expression_attribute_names['#delete_flag'] = 'delete_flag'

    # join update expressions
    update_expression = 'SET ' + ', '.join(update_expression)

    # try updating company 
    try:
        response = table.update_item(
            Key={
                'pk_company_id': company_parent_id,
                'sk_user_id': company_user_id
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
        'body': json.dumps(response_generator("successfully updated company data", "200"))
    }

# get a company
def get_company(parent_id, user_id):
    # add filter
    filter_expression = Attr('sk_user_id').eq(user_id) & Attr('pk_company_id').eq(parent_id)
    scan_params = {'FilterExpression': filter_expression}

    response = table.scan(**scan_params)
    items = response.get('Items', [])
    return items

# compare datetime
def is_date_time_equal(date_string_1, date_string_2):
    # Define the format of the date strings
    date_format = "%Y-%m-%dT%H:%M:%S.%f"

    # Parse the date strings into datetime objects
    date_1 = datetime.strptime(date_string_1, date_format)
    date_2 = datetime.strptime(date_string_2, date_format)

    return date_1 == date_2