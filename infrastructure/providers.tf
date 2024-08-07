
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

locals {

//////////////////////////////////////////////////////////////////////////////////////////////
/////////////  Substitute below values to match your AWS account, region & profile //////////////////////////////////////////////////////////////////////////////////////////////
  aws_account = "480361390441"   # AWS account
  aws_region  = "eu-west-3"      # AWS region
  aws_profile = "cgarcia" # AWS profile
 ///////////////////////////////////////////////////////////////////////////////////////////// 
  tfm_role = "arn:aws:iam::480361390441:role/TFM_Role"
  ecr_reg   = "${local.aws_account}.dkr.ecr.${local.aws_region}.amazonaws.com" # ECR docker registry URI
  ecr_repo  = var.ecr_bronze_products_repository_name
  ecr_repo_pipeline  = var.ecr_tfm-etl-pipeline_repository_name
  image_tag = "latest"

  dkr_img_src_path = "${path.module}/../src/infra/ecs_bronze_products"
  dkr_img_src_sha256 = sha256(join("", [for f in fileset(".", "${local.dkr_img_src_path}/**") : file(f)]))

  dkr_build_cmd = <<-EOT
        docker build -t ${local.ecr_reg}/${local.ecr_repo}:${local.image_tag} \
            -f ${local.dkr_img_src_path}/Dockerfile ./../

        
        aws ecr get-login-password --region ${local.aws_region}| docker login --username AWS --password-stdin ${local.ecr_reg}

        docker push ${local.ecr_reg}/${local.ecr_repo}:${local.image_tag}
    EOT

}
