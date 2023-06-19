import json
import boto3
import botocore.exceptions
from google.cloud import storage
import os,json

def lambda_handler(event, context):
    try:

        # Create a session with the desired region
        session = boto3.session.Session(region_name='us-east-1')
        # Initialize AWS Config client
        config = session.client('config')

        # Initialize the GCS client and bucket objects
        credential_dict = json.loads(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
        gcs_client = storage.Client.from_service_account_info(info=credential_dict)

        buckets = gcs_client.list_buckets()

        # Iterate over the buckets
        for bucket in buckets :
                bucket_name = bucket.name
    
                policy = bucket.get_iam_policy()
     
                # Prepare the list to store bindings
                bindings = []
            
                # Iterate over the bindings in the policy
                for binding in policy.bindings:
                        binding_data = {
                            'role': binding['role'],
                            'members': list(binding['members'])  # Convert set to list
                        }
                        bindings.append(binding_data)
                   
                            # Prepare the custom resource configuration item data
                resource_details = {
                    'bucketName':bucket_name,
                    'bindings': bindings
                }
            
                # Convert the resource details to JSON
                resource_details_json = json.dumps(resource_details)
            
                # Print the resource details
                print(resource_details_json)
            
                # Send the custom resource configuration item data to AWS Config
                config.put_resource_config(
                    ResourceType='Google::GCS::Bucket',
                    ResourceName=bucket_name,
                    ResourceId=bucket_name,
                    Configuration=resource_details_json,
                    Tags={},
                    SchemaVersionId='00000002'
                )

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise e