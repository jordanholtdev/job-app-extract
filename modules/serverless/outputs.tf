output "textract_sns_topic_arn" {
  value = aws_sns_topic.textract_sns_topic.arn
  
}

output "process_doc_lambda_arn" {
  value = aws_lambda_function.process_doc_lambda.arn
  
}

output "aws_lambda_permission" {
  value = aws_lambda_permission.s3_invoke_lambda
}