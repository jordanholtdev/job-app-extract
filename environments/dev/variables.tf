variable "region" {
  description = "the AWS region to deploy to"
  type        = string
  default     = "us-east-1"
}

variable "tags" {
  description = "the tags to apply to all resources"
  type        = map(string)
}

variable "source_bucket_name" {
  description = "the name of the S3 bucket to create"
  type        = string
  
}

variable "profile" {
  description = "the AWS profile to use"
  type        = string
  default     = "default"
  
}

variable "shared_config_files" {
  description = "the shared AWS config files to use"
  type        = list(string)
  default     = []
  
}

variable "shared_credentials_files" {
  description = "the shared AWS credentials files to use"
  type        = list(string)
  default     = []
  
}

variable "env" {
  description = "the environment to deploy to"
  type        = string
  default     = "dev"
  
}

