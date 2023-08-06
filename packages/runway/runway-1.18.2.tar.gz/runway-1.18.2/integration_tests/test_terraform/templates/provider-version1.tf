# Backend setup
terraform {
    backend "s3" {
      key = "terraform_test.tf"
    }
  }

# Variable definitions
  variable "region" {}

  # Provider and access setup
  provider "aws" {
    version = "~> 1.0"
    region = "${var.region}"
  }

# Data and resources
resource "aws_sqs_queue" "terraform_queue" {
  delay_seconds = 90
}
