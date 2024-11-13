import json
import os
import logging
import boto3
import uuid
import urllib.parse
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel("INFO")

s3_client = boto3.client('s3')
textract = boto3.client('textract')

def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event, indent=2))

    try:
        source_bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        key = urllib.parse.unquote_plus(key)  # Decode the URL-encoded object key

        logger.info("Analyzing document from S3 bucket: %s", source_bucket)
        logger.info('## KEY: ' + key)

        # Check if the object exists in the S3 bucket
        try:
            s3_client.head_object(Bucket=source_bucket, Key=key)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                logger.error(f"Object {key} does not exist in bucket {source_bucket}")
                return "Object not found"
            else:
                logger.error(f"Error checking object {key} in bucket {source_bucket}: {e}")
                return "Error checking object"

        # Copy the object to the local folder
        unique_name = str(uuid.uuid4()) + '-' + key.split('/')[-1]
        download_path = f'/tmp/{unique_name}'
        try:
            s3_client.download_file(source_bucket, key, download_path)
            if os.path.exists(download_path):
                logger.info(f"File downloaded successfully to {download_path}")
            else:
                logger.error(f"Failed to download file to {download_path}")
                return "File download failed"
        except ClientError as e:
            logger.error(f"Error downloading file {key} from bucket {source_bucket}: {e}")
            return "File download error"

        with open(download_path, 'rb') as document:
            document_bytes = document.read()

        # Start the document analysis
        try:
            response = textract.start_document_analysis(
                DocumentLocation={'S3Object': {'Bucket': source_bucket, 'Name': key}},
                FeatureTypes=["QUERIES"],
                NotificationChannel={
                    'RoleArn': os.environ['TEXTRACT_SNS_ROLE_ARN'],
                    'SNSTopicArn': os.environ['TEXTRACT_SNS_TOPIC_ARN']
                },
                QueriesConfig={
                    "Queries": [{
                        "Text": "What is the job title?",
                        "Alias": "JOB_TITLE"
                    }, {
                        "Text": "What is the company name?",
                        "Alias": "COMPANY_NAME" 
                    }, {
                       "Text": "What is the company website?",
                        "Alias": "COMPANY_WEBSITE"
                    }, {
                        "Text": "What are the job requirements?",
                        "Alias": "JOB_REQUIREMENTS"
                    },{
                       "Text": "What is the salary range?",
                        "Alias": "SALARY_RANGE"
                    },{
                       "Text": "What are the skills required for the job?",
                        "Alias": "SKILLS_REQUIRED"
                    }, {
                       "Text": "What is the job posting id",
                        "Alias": "JOB_POSTING_ID"
                    }, {
                        "Text": "What is the location?",
                          "Alias": "JOB_LOCATION"
                    }]
                }
            )

            job_id = response['JobId']
            logger.info(f"Started document analysis with JobId: {job_id}")

        except ClientError as e:
            logger.error(f"Error starting document analysis: {e}")
            return "Document analysis error"

        logger.info('## ENVIRONMENT VARIABLES')
        logger.info(os.environ['AWS_LAMBDA_LOG_GROUP_NAME'])
        logger.info(os.environ['AWS_LAMBDA_LOG_STREAM_NAME'])
        logger.info('## EVENT')
        return "Version 1.0.0"

    except Exception as e:
        logger.error(f"Error processing event: {e}")
        return "Error processing event"