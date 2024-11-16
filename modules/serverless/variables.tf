variable "lambda_role_arn" {
  description = "The ARN of the IAM role to be assumed by the Lambda function"
}

variable "textract_sns_topic_name" {
  description = "The name of the SNS topic to be created"
}

variable "textract_sns_role_arn" {
  description = "The ARN of the IAM role to be assumed by the SNS topic"
  
}

variable "source_bucket_arn" {
  description = "The ARN of the S3 bucket to be used as the source of the Lambda function"
}

variable "source_bucket_name" {
  description = "The name of the S3 bucket to be used as the source of the Lambda function"
}