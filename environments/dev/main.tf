terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }
  required_version = ">= 1.2.0"
}

provider "aws" {
  region                   = var.region
  shared_config_files      = var.shared_config_files
  shared_credentials_files = var.shared_credentials_files
  profile                  = var.profile

  default_tags {
    tags = var.tags
  }
}


module "storage" {
  source      = "../../modules/storage"
  source_bucket_name = "${var.env}-${var.source_bucket_name}"
  lambda_process_doc_arn = module.serverless.process_doc_lambda_arn
  lambda_permission_arn = module.serverless.aws_lambda_permission
  tags = merge(var.tags, {
    Name = "storage"
  })

}

module "iam" {
  source                 = "../../modules/iam"
  lambda_role_name       = "${var.env}-${var.tags.project}-lambda-role"
  textract_sns_role_name = "${var.env}-${var.tags.project}-textract-role"
  textract_sns_topic_arn = module.serverless.textract_sns_topic_arn
  source_bucket_arn      = module.storage.bucket_arn
  tags = merge(var.tags, {
    Name = "iam"
  })

}

module "serverless" {
  source                  = "../../modules/serverless"
  lambda_role_arn         = module.iam.lambda_role_arn
  textract_sns_topic_name = "AmazonTextract-${var.env}-${var.tags.project}-sns-topic"
  textract_sns_role_arn   = module.iam.textract_role_arn
  source_bucket_arn       = module.storage.bucket_arn
  source_bucket_name      = module.storage.bucket_name
}
