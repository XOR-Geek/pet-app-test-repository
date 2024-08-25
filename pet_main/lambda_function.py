import json
from image_upload import  image_upload_handler, pet_image_checker
from authentication import user_sign_in_handler,user_sign_up_handler,email_varify_handler,user_change_password_handler,email_sender,user_registration_handler
from member_info import user_details_handler,member_list_handler,user_update_handler
from pet_parent import admin_parent_list_handler, parent_add_handler,pet_parent_list_handler,pet_parent_details_handler,pet_parent_update_handler
from pet_child import admin_child_list_handler, pet_child_details_handler,pet_child_list_handler,pet_child_add_handler,pet_child_day_update_handler,outside_father_entry_handler,outside_father_update_handler,outside_father_details_handler
from pet_company import  admin_company_list_handler, admin_company_registration_handler, admin_company_update_handler, admin_edit_log_handler, admin_member_list_handler, company_details_handler
from pet_growth import view_growth_search_handler,view_growth_list_handler
from varient_data import pet_varient_data_handler
from parent_children import parent_children_handler

def lambda_handler(event, context):
    # #response=image_upload_handler(event)
    # return {
    #     #"statusCode": response["statusCode"],
    #     "body": json.dumps(event),
    #     #"headers": response["headers"]
    # }
    # return {
    #     "result":json.dumps(event.get('path', ''))
    # }
    print(event)
    
    resource = event['resource']

    if resource == "/image_upload":
        response=image_upload_handler(event)
    elif resource == "/pet_parent_add":
        response=parent_add_handler(event)
    elif resource == "/pet_parent_list":
        response=pet_parent_list_handler(event)
    elif resource == "/pet_parent_details":
        response=pet_parent_details_handler(event)
    elif resource == "/pet_parent_update":
        response=pet_parent_update_handler(event)  
    elif resource == "/sign_in":
        response=user_sign_in_handler(event)
    elif resource == "/sign_up":
        response=user_sign_up_handler(event)         
    elif resource == "/email_verification":
        response=email_varify_handler(event)
    elif resource == "/user_details":
        response=user_details_handler(event)
    elif resource == "/company_member_list":
        response=member_list_handler(event)
    elif resource == "/user_update":
        response=user_update_handler(event)
    elif resource == "/pet_child_details":
        response=pet_child_details_handler(event)  
    elif resource == "/pet_child_list":
        response=pet_child_list_handler(event)
    elif resource == "/pet_child_add":
        response=pet_child_add_handler(event)     
    elif resource == "/pet_child_day_update":
        response=pet_child_day_update_handler(event)
    elif resource == "/outside_father_add":
        response=outside_father_entry_handler(event)
    elif resource == "/outside_father_update":
        response=outside_father_update_handler(event) 
    elif resource == "/outside_father_details":
        response=outside_father_details_handler(event) 
    elif resource == "/company_details":
        response=company_details_handler(event)
    elif resource == "/pet_view_growth_list":
        response=view_growth_list_handler(event)
    elif resource == "/pet_view_growth_search":
        response=view_growth_search_handler(event)         
    elif resource == "/pet_image_checker":
        response=pet_image_checker(event)       
    elif resource == "/admin_child_list":
        response=admin_child_list_handler(event)      
    elif resource == "/admin_company_list":
        response=admin_company_list_handler(event)          
    elif resource == "/admin_member_list":
        response=admin_member_list_handler(event)     
    elif resource == "/admin_parent_list":
        response=admin_parent_list_handler(event)     
    elif resource == "/admin_edit_log_list":
        response=admin_edit_log_handler(event)         
    elif resource =="/pet_varient_data":
        response = pet_varient_data_handler(event)       
    elif resource == "/parent_children":
        response = parent_children_handler(event)   
    elif resource == "/change_password":
        response = user_change_password_handler(event)   
    elif resource == "/send_email":
        response = email_sender(event)  
    elif resource == "/user_register":
        response = user_registration_handler(event) 
    elif resource == "/company_add":
        response=admin_company_registration_handler(event) 
    elif resource == "/admin_company_update":
        response=admin_company_update_handler(event)
    elif resource == "/admin_parent_details":
        response=pet_parent_details_handler(event)
    elif resource == "/admin_parent_update":
        response=pet_parent_update_handler(event)
    elif resource == "/admin_child_details":
        response=pet_child_details_handler(event)                                                   
    else:
        return {
            "statusCode": 400,
            "body": "Invalid endpoint"
        }

    return {
         "statusCode": response["statusCode"],
         "body": response["body"]
     }





  