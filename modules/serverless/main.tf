data "archive_file" "lambda_zip" {
  type             = "zip"
  source_file      = "${path.module}/lambda/process-function/index.py"
  output_file_mode = "0666"
  output_path      = "${path.module}/files/lambda-process-deployment.zip"
}

data "archive_file" "results_lambda_zip" {
  type             = "zip"
  source_dir       = "${path.module}/lambda/results-function"
  output_file_mode = "0666"
  output_path      = "${path.module}/files/lambda-results-deployment.zip"
}

resource "aws_lambda_function" "process_doc_lambda" {
  filename      = "${path.module}/files/lambda-process-deployment.zip"
  function_name = "processdoc"
  role          = var.lambda_role_arn
  handler       = "index.lambda_handler"
  runtime       = "python3.10"
  timeout       = 120


  environment {
    variables = {
      TEXTRACT_SNS_ROLE_ARN  = var.textract_sns_role_arn
      TEXTRACT_SNS_TOPIC_ARN = aws_sns_topic.textract_sns_topic.arn
    }
  }
}

resource "aws_lambda_permission" "s3_invoke_lambda" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.process_doc_lambda.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = var.source_bucket_arn
}

resource "aws_sns_topic" "textract_sns_topic" {
  name = var.textract_sns_topic_name
}

resource "aws_sns_topic_subscription" "process_result_subscription" {
  topic_arn = aws_sns_topic.textract_sns_topic.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.process_result_lambda.arn
}

resource "aws_lambda_function" "process_result_lambda" {
  filename      = "${path.module}/files/lambda-results-deployment.zip"
  function_name = "processresult"
  role          = var.lambda_role_arn
  handler       = "index.lambda_handler"
  runtime       = "python3.10"
  timeout       = 120
}

resource "aws_cloudwatch_log_group" "processresult_log_group" {
  name              = "/aws/lambda/processresult"
  retention_in_days = 14
}
