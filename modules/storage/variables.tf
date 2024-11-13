variable "bucket_name" {
  description = "The name of the S3 bucket"
  type = string
}

variable "tags" {
  description = "Tags to apply to the S3 bucket"
  type = map(string)
}

variable "lambda_process_doc_arn" {
  description = "lambda_process_doc_arn"
}

variable "lambda_permission_arn" {
  description = "lambda_permissoin_arn"
  
}