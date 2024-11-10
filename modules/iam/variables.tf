variable "tags" {
  description = "the tags to apply to all resources"
  type        = map(string)
  
}

variable "lambda_role_name" {
  description = "the name of the IAM role for the Lambda function"
  type        = string
  
}

variable "source_bucket_arn" {
  description = "the ARN of the source bucket"
  type        = string
  
}

variable "textract_sns_role_name" {
  description = "the name of the IAM role for the Textract function"
  type        = string
  
}

variable "textract_sns_topic_arn" {
  description = "The ARN of the SNS topic"
}