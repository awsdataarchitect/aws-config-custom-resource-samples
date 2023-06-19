import json
import boto3
import botocore.exceptions
import os,json
from datetime import datetime


def lambda_handler(event, context):

    # Print the entire event payload
    #print(json.dumps(event))

    # Parse the invoking event string as JSON
    invoking_event = json.loads(event['invokingEvent'])
    #print(invoking_event)

    try:
        # Initialize AWS Config client
        config = boto3.client('config')

        # Get properties from the event
        bucketName = invoking_event['configurationItem']['resourceId']

        # Get configuration history for the Google Storage Bucket Resource
        response = config.get_resource_config_history(
            resourceType='Google::GCS::Bucket',
            resourceId=bucketName
        )

        # Get the most recent configuration
        current_config = json.loads(response['configurationItems'][0]['configuration'])
     
        # Check if the GCS bucket is public

        is_public = False
        for binding in current_config['bindings']:
            if binding['role'] == 'roles/storage.objectViewer' and ('allUsers' in binding['members'] or '*' in binding['members']):
                is_public = True
                break


        if is_public:
            # If the bucket is public, mark it as non-compliant
            evaluations = [
                {
                    'ComplianceResourceType': invoking_event['configurationItem']['resourceType'],
                    'ComplianceResourceId': bucketName,
                    'ComplianceType': 'NON_COMPLIANT',
                    'Annotation': 'The GCS bucket has public access.',
                    'OrderingTimestamp': datetime.now()
                }
            ]
        else:
            # If the bucket is not public, mark it as compliant
            evaluations = [
                {
                    'ComplianceResourceType': invoking_event['configurationItem']['resourceType'],
                    'ComplianceResourceId': bucketName,
                    'ComplianceType': 'COMPLIANT',
                    'Annotation': 'The GCS bucket does not have public access.',
                    'OrderingTimestamp': datetime.now()
                }
            ]

        # Send the evaluations to AWS Config
        config.put_evaluations(
                Evaluations=evaluations,
                ResultToken=event['resultToken']
            )

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise e
