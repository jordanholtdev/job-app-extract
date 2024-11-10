variable "vpc_cidr_block" {
  description = "CIDR block for the VPC"
}

variable "network_tags" {
  description = "Tags to apply to the VPC"
  type        = map(string)
}