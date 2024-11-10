resource "aws_s3_bucket" "source_bucket" {
  bucket = var.bucket_name

  tags = merge(var.tags)
}