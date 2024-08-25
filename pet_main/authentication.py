import json
import time
import boto3
import logging
from common import CommonConfig
from datetime import datetime
from pet_company import admin_company_registration_handler
from botocore.exceptions import ClientError
from datetime import datetime

# Initialize clients for Cognito and DynamoDB
cognito_client = boto3.client('cognito-idp')
dynamodb_client = boto3.client('dynamodb')
ses_client = boto3.client('ses', region_name='ap-south-1')



def user_sign_in_handler(event):
    try:
        event = json.loads(event.get('body', '{}'))
        email = event['email']
        password = event['password']
    except KeyError as e:
        return {
            'statusCode': 200,
            'body': json.dumps({
                'statusCode': "400",
                "body":{
  'error': f'Missing parameter: {str(e)}'
                }
              })
        }

    try:
        # Initiate authentication
        response = cognito_client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password
            },
            ClientId=CommonConfig.cognito_client_id  # Replace with your App Client ID
        )

        # Retrieve tokens
        id_token = response['AuthenticationResult']['IdToken']
        access_token = response['AuthenticationResult']['AccessToken']
        refresh_token = response['AuthenticationResult']['RefreshToken']

        # Get user details
        user_response = cognito_client.get_user(
            AccessToken=access_token
        )

        # Extract user ID (sub)
        user_id = None
        for attribute in user_response['UserAttributes']:
            if attribute['Name'] == 'sub':
                user_id = attribute['Value']
                break

        if not user_id:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    
                    'statusCode': "400",
                    "body":{
 'error': 'User ID not found'
                    }
                   
                    
                    })
            }

        # Retrieve user details from DynamoDB
        dynamodb_response = dynamodb_client.get_item(
            TableName=CommonConfig.pet_user_tablename,
            Key={
                'pk_user_id': {'S': user_id}
            }
        )

        if 'Item' not in dynamodb_response:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'statusCode': "400",
                    'body':{
'error': 'User details not found in database'
                    }
                    })
            }

        # Extract delete_flag and status
        delete_flag = int(dynamodb_response['Item']['delete_flag']['S'])
        status = int(dynamodb_response['Item']['status']['S'])

        if delete_flag == 1:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'statusCode': "403",
                    "body":{
 'error': 'Account has been disabled, please contact with admin to restore your account'
                    }
                   })
            }
        elif delete_flag == 0 and status == 0:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'statusCode': "403",
                    "body":{
 'error': 'Account is not activated yet. Please wait for a while'
                    }
                   })
            }
        elif delete_flag == 0 and status == 1:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'statusCode': "200",
                    "body":{
                    'message': 'Authentication successful',
                    'user_id': user_id,
                    'id_token': id_token,
                    'access_token':access_token
                    }
                    
                    # ,'access_token': access_token,
                    # 'refresh_token': refresh_token
                })
            }
        else:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'statusCode': "400",
                    "body":{
'error': 'Invalid account status'
                    }
                    })
            }
    except ClientError as e:
        return {
            'statusCode': 200,
            'body': json.dumps({
                'statusCode': "400",
                "body":{
 'error': e.response['Error']['Message']
                }
               })
        }
    
def user_sign_up_handler(event):
    try:
        event = json.loads(event.get('body', '{}'))
        email = event['email']
        user_role = event['user_role']
        user_name = event['user_name']
        company_name = event['company_name']
        company_id = event['comapny_id']
        status = str(event['status'])  # Convert status to string if it's a number
        delete_flag = str(event['delete_flag'])  # Convert delete_flag to string if it's a number
        park_id = event['park_id'] # Convert delete_flag to string if it's a number# Convert delete_flag to string if it's a number
        result = verify_email_exists(email)
        if(result):
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'statusCode': "400",
                    "body": {
                        'message': 'Email already exists',
                        'exists': True
                    }
                })
            }
        partition_key = generate_parent_key(company_id)

        item = {
            'pk_user_id': {'S': partition_key},  # String type
            'sk_id': {'S': company_id},  # String type
            'email': {'S': email},  # String type
            'role': {'S': user_role},  # String type
            'user_name': {'S': user_name},  # String type
            'company_name': {'S': company_name},  # String type
            'park_id': {'S': park_id},  # String type
            # 'member_ship_no': {'S': member_ship_no},  # String type
            'phone': {'S': ''},  # Empty string
            'location': {'S': ''},  # Empty string
            'user_verify_flag':{'S': '0'},
            'delete_flag': {'S': delete_flag},  # String type
            'status': {'S': status},  # String type
            'created_at': {'S': datetime.utcnow().isoformat()},  # String type with ISO 8601 format
            'updated_at': {'S': datetime.utcnow().isoformat()},  # String type with ISO 8601 format
            'profile_img': {'S': ''}  # Empty string
        }

        dynamodb_client.put_item(
            TableName=CommonConfig.temp_pet_user_tablename,
            Item=item
        )
        email_event = {
            'body': json.dumps({
                'to_email': email,
                'subject': '【ブリレコアプリ】本登録のお願い',
                'body': '△△様◯◯様よりブリレコへの招待がありました。以下のリンクをタップして、アプリをインストール後、登録を完了してください。https://pet.xorgeek.com?id='+partition_key,
                'from_email': 'dev.xorgeek@gmail.com'  # Replace with your verified email
            })
        }

        # Call the email sender function
        email_sender(email_event)
        return {
            'statusCode': 200,
            'body': json.dumps({
                'statusCode': "200",
                "body": {
                
                    'message': 'User successfully  verified and waiting for passsword setup '
                }
            })
        }

    except ClientError as e:
        return {
            'statusCode': 200,
            'body': json.dumps({
                'statusCode': "400",
                "body": {
                    'error': e.response['Error']['Message']
                }
            })
        }
def email_varify_handler(event):
    client = boto3.client('cognito-idp')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(CommonConfig.pet_user_tablename)
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()

    logger.info(f"Received event: {json.dumps(event)}")

    try:
        event = json.loads(event.get('body', '{}'))
        email = event['email']
        code = event['code']
    except KeyError as e:
        return {
            'statusCode': 200,
            'body': json.dumps({
                'statusCode': "400",
                "body":{
'error': f'Missing parameter: {str(e)}'
                }
                })
        }

    try:
        # Confirm the user's email
        response = client.confirm_sign_up(
            ClientId=CommonConfig.cognito_client_id,  # Replace with your App Client ID
            Username=email,  # Email used as the username
            ConfirmationCode=code
        )
        
        # Fetch user details
        user_response = client.admin_get_user(
            UserPoolId=CommonConfig.cognito_userpool_id,  # Replace with your User Pool ID
            Username=email
        )
        
        # Extract the user ID from the response
        user_id = None
        for attribute in user_response['UserAttributes']:
            if attribute['Name'] == 'sub':
                user_id = attribute['Value']
                break
            
        item = {
            'pk_user_id': user_id,
            'sk_id': '2001',
            'email': email,
            'role':'0',
            'name' : '',
            'phone' : '',
            'location':'',
            'delete_flag':'0',
            'status': '1',
            'created_at':'',
            'updated_at':'',
            'profile_img':''
        }    
        
        response = table.put_item(Item=item)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                  'statusCode': "200",
                  "body":{
                       'message': 'User successfully verified', 'user_id': user_id
                  }
               })
        }
    except ClientError as e:
        return {
            'statusCode': 200,
            'body': json.dumps({
                  'statusCode': "400",
                  "body":{
                     'error': e.response['Error']['Message']  
                  }
               })
        }
    
def user_change_password_handler(event):
    try:
        event = json.loads(event.get('body', '{}'))
        access_token = event['access_token']
        old_password = event['old_password']
        new_password = event['new_password']

        # User change password
        cognito_client.change_password(
            PreviousPassword=old_password,
            ProposedPassword=new_password,
            AccessToken=access_token
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'statusCode': "200",
                "body": {
                    'message': 'Password changed successfully'
                }
            })
        }

    except ClientError as e:
        return {
            'statusCode': 200,
            'body': json.dumps({
                'statusCode': "400",
                "body": {
                    'error': e.response['Error']['Message']
                }
            })
        }
def verify_email_exists(email):

    try:
        response = cognito_client.list_users(
            UserPoolId=CommonConfig.cognito_userpool_id,  # Replace with your User Pool ID
            Filter=f'email = "{email}"',
            Limit=1
        )

        if response['Users']:
            # Email exists
            return True
        else:
            # Email does not exist
            return False

    except ClientError as e:
        raise e        
def generate_parent_key(sort_key):
    last_four = sort_key[-4:]
    unix_timestamp = int(time.time())
    sort_key = f"{last_four}{unix_timestamp}"
    return sort_key

def email_sender(event):
    """
    Lambda function to send an email using Amazon SES. 
    Extracts email details from the event object.

    :param event: The event object from API Gateway
    :param context: The Lambda context object
    :return: API Gateway response object
    """
    try:
        # Extract email details from the event body
        body = json.loads(event.get('body', '{}'))
        to_email = body.get('to_email')
        subject = body.get('subject')
        email_body = body.get('body')
        from_email = body.get('from_email', 'dev.xorgeek@gmail.com')  # Default sender email

        if not all([to_email, subject, email_body]):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required fields: to_email, subject, and body'})
            }

        # Prepare the email request
        response = ses_client.send_email(
            Source=from_email,
            Destination={
                'ToAddresses': [to_email]
            },
            Message={
                'Subject': {
                    'Data': subject
                },
                'Body': {
                    'Text': {
                        'Data': email_body
                    }
                }
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f"Email sent successfully to {to_email}",
                'ses_response': response
            })
        }

    except ClientError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f"Failed to send email: {e.response['Error']['Message']}"})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f"Internal server error: {str(e)}"})
        }
   
def user_registration_handler(event):
    event = json.loads(event.get('body', '{}'))
    temp_id = event['temp_id']
    password = event['password']
    
    # Initialize the AWS services clients
    cognito_client = boto3.client('cognito-idp')
    dynamodb = boto3.resource('dynamodb')
    
    # DynamoDB table names
    temp_table_name = CommonConfig.temp_pet_user_tablename
    target_table_name = CommonConfig.pet_user_tablename
    
     # Step 1: Retrieve data from the temp_table using temp_id
    temp_table = dynamodb.Table(temp_table_name)
    temp_data = temp_table.get_item(Key={'pk_user_id': temp_id})
    item_to_insert = temp_data['Item']
    email=item_to_insert['email']

    if 'Item' not in temp_data:
            return {
                'statusCode': 400,
                'body': json.dumps({
                      'statusCode': 400,
                    'error': 'Temp ID not found in temp table'
                })
            }
    try:
        # Cognito sign-up
        response = cognito_client.sign_up(
            ClientId=CommonConfig.cognito_client_id,
            Username=email,
            Password=password,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': email
                }
            ]
        )

        # Automatically confirm the user
        cognito_client.admin_confirm_sign_up(
            UserPoolId=CommonConfig.cognito_userpool_id,
            Username=email
        )

        # Get the Cognito user ID
        user_response = cognito_client.admin_get_user(
            UserPoolId=CommonConfig.cognito_userpool_id,
            Username=email
        )

        # Extract the user ID (sub attribute)
        user_id = None
        for attribute in user_response['UserAttributes']:
            if attribute['Name'] == 'sub':
                user_id = attribute['Value']
                break

        if not user_id:
            return {
                'statusCode': 400,
                'body': json.dumps({
                      'statusCode': 400,
                    'error': 'User ID not found'
                })
            }

       

        # Step 2: Insert the retrieved data into the target table
        target_table = dynamodb.Table(target_table_name)
        item_to_insert = temp_data['Item']
        
        # Remove 'pk_user_id' and add 'user_id'
        item_to_insert.pop('pk_user_id', None)  # Remove the old primary key
        item_to_insert['pk_user_id'] = user_id  # Assign the new user ID as the primary key
        company_event = {
            'body': json.dumps({
                "company_id":item_to_insert['sk_id'],
                "name": item_to_insert['company_name'],
                "representative_name": item_to_insert['user_name'],
                "email": item_to_insert['email'],
                "affiliated_park":  item_to_insert['park_id']
                       })
        }
        
        admin_company_registration_handler(company_event)



        # Insert the modified item into the target table
        target_table.put_item(Item=item_to_insert)
        temp_table.update_item(
        Key={'pk_user_id': temp_id},
        UpdateExpression="SET user_verify_flag = :val",
        ExpressionAttributeValues={
            ':val': "1"
        }
        )
   

        return {
            'statusCode': 200,
            'body': json.dumps({
                'statusCode': 200,
                'message': 'User registered successfully'
            })
        }

    except ClientError as e:
        return {
            'statusCode': 400,
                'body': json.dumps({
                     'statusCode': 400,
                     'error': e.response['Error']['Message']
                })
        }
    
# checking again here change here
# some comments here
