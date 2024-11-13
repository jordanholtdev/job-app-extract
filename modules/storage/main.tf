resource "aws_s3_bucket" "source_bucket" {
  bucket = var.source_bucket_name

  tags = merge(var.tags)
}

resource "aws_s3_bucket_notification" "source_bucket_notification" {
  bucket = aws_s3_bucket.source_bucket.bucket

  lambda_function {
    lambda_function_arn = var.lambda_process_doc_arn 
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".pdf"
  }

  depends_on = [
    var.lambda_permission_arn
  ]
}