terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket = "cgarcia.cidaen.tfm.terraform"
    key  = "state/terraform.tfstate"
    region = "eu-west-3"
    encrypt = true
  }
}

# Configure the AWS Provider
provider "aws" {
  region = "eu-west-3"
}