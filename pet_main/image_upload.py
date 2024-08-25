import base64
import json
import boto3
import time
import random
from common import CommonConfig
from mimetypes import guess_extension, guess_type

client = boto3.client('s3')
rekognition_client = boto3.client('rekognition')
REGION_NAME = "ap-south-1"
BUCKET_NAME = CommonConfig.s3_bucketname

def image_upload_handler(event):
    # Check if the body is base64-encoded
    if event.get("isBase64Encoded"):
        # Decode the base64-encoded body
        decoded_body = base64.b64decode(event["body"])
    else:
        decoded_body = event["body"].encode()

    # Get the boundary from the content type header
    content_type = event["headers"].get("Content-Type") or event["headers"].get("content-type")
    boundary = content_type.split("boundary=")[-1]

    # Split the body using the boundary
    boundary_bytes = ("--" + boundary).encode()
    parts = decoded_body.split(boundary_bytes)

    # Prepare a dictionary to hold the parsed data
    parsed_data = {}

    for part in parts:
        if part.strip() == b"" or part.strip() == b"--":
            continue

        # Split the headers and body
        headers, body = part.split(b"\r\n\r\n", 1)
        body = body.rstrip(b"\r\n")

        # Parse the headers
        header_lines = headers.split(b"\r\n")
        headers_dict = {}
        for header in header_lines:
            if b": " in header:
                name, value = header.split(b": ", 1)
                headers_dict[name.lower()] = value

        # Extract the content disposition
        content_disposition = headers_dict.get(b"content-disposition", b"").decode()
        disposition_parts = content_disposition.split("; ")
        disposition_info = {}
        for disp_part in disposition_parts:
            if "=" in disp_part:
                name, value = disp_part.split("=", 1)
                disposition_info[name] = value.strip('"')

        # Get the field name
        field_name = disposition_info.get("name")

        if not field_name:
            continue

        # Check if it's a file
        filename = disposition_info.get("filename")
        
        if filename:
            # It's a file
            # Check MIME type to ensure it's an image
            mime_type = guess_type(filename)[0]
            if not mime_type or not mime_type.startswith('image/'):
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Only image files are allowed"}),
                    "headers": {
                        "Content-Type": "application/json"
                    }
                }

            # Decode the file content
            ms = base64.b64decode(base64.b64encode(body).decode('utf-8'))
            # Delay the URL construction until we have userid and companyid
            parsed_data[field_name] = {
                "filename": filename,
                "content": ms
            }
        else:
            # It's a regular form field
            parsed_data[field_name] = body.decode('utf-8')

    # Extract userid and companyid from the parsed data
    userid = parsed_data.get('user_id')
    companyid = parsed_data.get('company_id')

    if not userid or not companyid:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "user_id and company_id are required"}),
            "headers": {
                "Content-Type": "application/json"
            }
        }

    # Collect image paths
    image_paths = {}
    image_index = 1

    # Now that we have both ids, we can upload the file
    for field_name, value in parsed_data.items():
        if isinstance(value, dict) and 'filename' in value:
            original_filename = value['filename']
            content = value['content']

            # Get the file extension from the original filename
            file_extension = guess_extension(guess_type(original_filename)[0])
            if not file_extension:
                file_extension = '.jpg'  # Default to .jpg if extension cannot be determined

            # Generate the filename in the required format
            timestamp = int(time.time())
            random_number = random.randint(1000, 9999)
            filename = f"{timestamp}_{random_number}_{userid}{file_extension}"
            url = upload_image(content, companyid, userid, filename)
            image_paths[f"path{image_index}"] = url
            image_index += 1

    # Construct the response
    response_body = {
        "statusCode":200,
        "body": image_paths
    }

    return {
        "statusCode": 200,
        "body": json.dumps(response_body)
    }

def upload_image(content, companyid, userid, filename):
    # Create the folder structure and upload the image
    try:
        s3_key = f"{companyid}/{userid}/{filename}"
        response = client.put_object(
            Body=content,
            Bucket=BUCKET_NAME,
            Key=s3_key
        )
        # Construct the S3 URL
        s3_path = f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
        return s3_path
    except Exception as e:
        print(f"Error uploading file: {e}")
        raise

def pet_image_checker(event):
    try:
        # Check if the body is base64-encoded
        if event.get("isBase64Encoded"):
            # Decode the base64-encoded body
            decoded_body = base64.b64decode(event["body"])
        else:
            decoded_body = event["body"].encode()

        # Get the boundary from the content type header
        content_type = event["headers"].get("Content-Type") or event["headers"].get("content-type")
        boundary = content_type.split("boundary=")[-1]

        # Split the body using the boundary
        boundary_bytes = ("--" + boundary).encode()
        parts = decoded_body.split(boundary_bytes)

        # Prepare a list to hold the parsed data and error messages
        parsed_data = []
        error_messages = []

        image_count = 0
        valid_images = True  # Flag to track if all images are valid

        for index, part in enumerate(parts):
            if part.strip() == b"" or part.strip() == b"--":
                continue

            # Split the headers and body
            headers, body = part.split(b"\r\n\r\n", 1)
            body = body.rstrip(b"\r\n")

            # Parse the headers
            header_lines = headers.split(b"\r\n")
            headers_dict = {}
            for header in header_lines:
                if b": " in header:
                    name, value = header.split(b": ", 1)
                    headers_dict[name.lower()] = value

            # Extract the content disposition
            content_disposition = headers_dict.get(b"content-disposition", b"").decode()
            disposition_parts = content_disposition.split("; ")
            disposition_info = {}
            for disp_part in disposition_parts:
                if "=" in disp_part:
                    name, value = disp_part.split("=", 1)
                    disposition_info[name] = value.strip('"')

            # Get the field name
            field_name = disposition_info.get("name")

            if not field_name:
                continue

            # Check if it's a file
            filename = disposition_info.get("filename")
            
            if filename:
                # It's a file
                # Check MIME type to ensure it's an image
                mime_type = guess_type(filename)[0]
                if not mime_type or not mime_type.startswith('image/'):
                    error_messages.append(f"Invalid MIME type for image {filename}")
                    continue

                # The image content should be used directly without base64 decoding
                image_content = body

                # Check image labels with Rekognition
                labels = detect_labels(image_content)
                if not any(label.lower() in ["cat", "dog", "kitten", "puppy"] for label in labels):
                    error_messages.append(f"Image No {index}: Image {filename} is not a cat or dog.")
                    valid_images = False
                    continue

                # Generate a unique filename
                file_extension = guess_extension(mime_type)
                if not file_extension:
                    file_extension = '.jpg'  # Default to .jpg if extension cannot be determined

                timestamp = int(time.time())
                random_number = random.randint(1000, 9999)
                s3_key = f"{timestamp}{random_number}{file_extension}"

                # Store uploaded image path for later upload
                parsed_data.append({
                    "field_name": field_name,
                    "filename": filename,
                    "image_content": image_content,
                    "s3_key": s3_key
                })

                image_count += 1

                # Limit to 3 images
                if image_count >= 3:
                    break

        if not valid_images:
            # Return 400 Bad Request with error messages
            return {
                "statusCode": 200,
                #doc_cat detection:
                "body": json.dumps({
                "statusCode": 400,
                "body": {
                    "errors": error_messages
                        }
                     }
                ),
                "headers": {
                    "Content-Type": "application/json"
                }
            }

        # Upload images to S3
        for data in parsed_data:
            fetch_url(data["image_content"], data["s3_key"])

        # Construct the response body with image URLs
        response_body = {
            "statusCode": 200,
            "body": [{"filename": data["filename"], "url": f"https://{BUCKET_NAME}.s3.{REGION_NAME}.amazonaws.com/{data['s3_key']}"} for data in parsed_data]
        }

        return {
            "statusCode": 200,
            "body": json.dumps(response_body),
            "headers": {
                "Content-Type": "application/json"
            }
        }

    except Exception as e:
        # Handle any exceptions
        error_message = f"Error processing request: {str(e)}"
        print(error_message)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": error_message}),
            "headers": {
                "Content-Type": "application/json"
            }
        }

def detect_labels(image_content):
    response = rekognition_client.detect_labels(Image={"Bytes": image_content}, MaxLabels=10, MinConfidence=90)
    labels = [label["Name"] for label in response["Labels"]]
    return labels

def fetch_url(content, filename):
    try:
        #fetch url"
        s3_url = f"https://{BUCKET_NAME}.s3.{REGION_NAME}.amazonaws.com/{filename}"
        return s3_url
    except Exception as e:
        # Handle upload errors
        print(f"Error uploading file to S3: {str(e)}")
        raise
