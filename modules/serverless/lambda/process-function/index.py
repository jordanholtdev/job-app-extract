import json
import os 
import logging
import uuid
import boto3

logger = logging.getLogger()
logger.setLevel("INFO")

s3_client = boto3.client('s3')
textract = boto3.client('textract')

def lambda_handler(event, context):
    
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    logger.info("Analyzing document from S3 bucket: %s", source_bucket)
    logger.info('## KEY: ' + key)


    # Copy the object to the local folder
    unique_name = str(uuid.uuid4()) + '-' + key.split('/')[-1]
    download_path = f'/tmp/{unique_name}'
    s3_client.download_file(source_bucket, key, download_path)
    if os.path.exists(download_path):
      logger.info(f"File downloaded successfully to {download_path}")
    else:
      logger.error(f"Failed to download file to {download_path}")
    
    with open(download_path, 'rb') as document:
      document_bytes = document.read()

    # Start the document analysis
    response = textract.start_document_analysis(
        DocumentLocation={'S3Object': {'Bucket': source_bucket, 'Name': key}},
        FeatureTypes=["QUERIES"],
        NotificationChannel={
            'RoleArn': os.environ['TEXTRACT_SNS_ROLE_ARN'],
            'SNSTopicArn': os.environ['TEXTRACT_SNS_TOPIC_ARN']
        },
        QueriesConfig={
            "Queries": [{
                "Text": "What is the job title",
                "Alias": "JOB_TITLE"
            }, {
                "Text": "What are the job requirements",
                "Alias": "JOB_REQUIREMENTS"
            }]
        }
    )

    job_id = response['JobId']
    logger.info(f"Started document analysis with JobId: {job_id}")

    logger.info('## ENVIRONMENT VARIABLES')
    logger.info(os.environ['AWS_LAMBDA_LOG_GROUP_NAME'])
    logger.info(os.environ['AWS_LAMBDA_LOG_STREAM_NAME'])
    logger.info('## EVENT')
    return "Version 1.0.0"