output "account_id" {
  value = data.aws_caller_identity.current.account_id
}

output "lambda_role_arn" {
  value = aws_iam_role.lambda_role.arn
  
}

output "textract_role_arn" {
  value = aws_iam_role.textract_sns_role.arn
}