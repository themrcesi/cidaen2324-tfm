############################## IAM ROLE ###############################
module "iam" {
  source = "./iam"
  region = local.aws_region
}


########################### S3 BUCKETS ############################

resource "aws_s3_bucket" "datalake" {
  bucket = "cgarcia.cidaen.tfm.datalake"
}

resource "aws_s3_bucket_lifecycle_configuration" "bucket-config" {
  bucket = aws_s3_bucket.datalake.id

  rule {
    id = "raw"

    filter {
        prefix = "raw/"
    }

    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 60
      storage_class = "GLACIER"
    }
  }

  rule {
    id = "bronze"

    filter {
      prefix = "bronze/"
    }

    transition {
      days          = 60
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 120
      storage_class = "GLACIER"
    }

    status = "Enabled"
  }
}

resource "aws_s3_bucket" "utils" {
  bucket = var.utils_s3_bucket
}

########################## LAMBDA LAYER ############################

data "archive_file" "create_layer_zip" {
  type             = "zip"
  source_dir      = "${path.module}/../src/etl"
  output_path      = "${path.module}/etl_layer.zip"
}

# Upload the ZIP file to S3
resource "aws_s3_object" "layer_zip" {
  depends_on = [data.archive_file.create_layer_zip, aws_s3_bucket.utils]

  bucket = var.utils_s3_bucket
  key    = var.utils_s3_bucket_layer_key
  source = "${path.module}/etl_layer.zip"
  acl    = "private"
}

resource "null_resource" "cleanup_layer_zip" {
  depends_on = [ aws_s3_object.layer_zip ]
  provisioner "local-exec" {
    command = <<EOT
      rm -f "${path.module}/etl_layer.zip"
    EOT
  }
  triggers = {
    always_run = "${timestamp()}"
  }
}

# Create the Lambda layer
resource "aws_lambda_layer_version" "etl_layer" {
  depends_on = [aws_s3_object.layer_zip]

  layer_name  = "cidaen2324-tfm-etl-layer"
  s3_bucket   = var.utils_s3_bucket
  s3_key      = var.utils_s3_bucket_layer_key
  compatible_runtimes = [var.utils_s3_bucket_layer_runtime]
  compatible_architectures = ["arm64"]

  lifecycle {
    create_before_destroy = true
  }
}

########################## ECR & ECR ###############################

resource "aws_ecr_repository" "bronze_products" {
  name                 = var.ecr_bronze_products_repository_name
  image_tag_mutability = "MUTABLE"   # Optional: Set to IMMUTABLE if you want image tags to be immutable
}

resource "aws_ecr_repository" "tfm-etl-pipeline" {
  name                 = var.ecr_tfm-etl-pipeline_repository_name
  image_tag_mutability = "MUTABLE"   # Optional: Set to IMMUTABLE if you want image tags to be immutable
}

resource "aws_ecs_cluster" "fargate_cluster" {
  name = var.ecs_pipeline_cluster_name
}

resource "null_resource" "build_push_dkr_img" {
  provisioner "local-exec" {
    command = local.dkr_build_cmd
  }

  triggers = {
    image_uri = "${local.ecr_reg}/${local.ecr_repo}:${local.image_tag}"
  }
}

resource "aws_ecs_task_definition" "bronze_products" {
  family                   = var.ecs_bronze_products_task_family_name
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "1024"  # 1 vCPU
  memory                   = "8192"  # 8 GB
  task_role_arn            = local.tfm_role
  execution_role_arn       = local.tfm_role

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "ARM64"
  }

  container_definitions = jsonencode([
    {
      name      = var.ecs_bronze_products_task_family_name
      image     = null_resource.build_push_dkr_img.triggers.image_uri
      essential = true
      cpu       = 1024  # 1 vCPU
      memory    = 8192  # 8 GB

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/bronze_products"
          "awslogs-region"        = local.aws_region  # Change as needed
          "awslogs-stream-prefix" = "ecs"
          "awslogs-create-group"  = "true"
        }
      }
    }
  ])
}

resource "aws_ecs_task_definition" "tfm-etl-pipeline" {
  family                   = var.ecs_tfm-etl-pipeline_task_family_name
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"  # 1 vCPU
  memory                   = "2048"  # 8 GB
  task_role_arn            = local.tfm_role
  execution_role_arn       = local.tfm_role

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "ARM64"
  }

  container_definitions = jsonencode([
    {
      name      = var.ecs_tfm-etl-pipeline_task_family_name
      image     = "${local.ecr_reg}/${local.ecr_repo_pipeline}:${local.image_tag}"
      essential = true

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/${var.ecs_tfm-etl-pipeline_task_family_name}"
          "awslogs-region"        = local.aws_region  # Change as needed
          "awslogs-stream-prefix" = "ecs"
          "awslogs-create-group"  = "true"
        }
      }
    }
  ])
}

############################## LAMBDAS ###################################
module "raw_categories" {
  source = "./lambdas"
  lambda_fn_name = "raw_download_categories"
  lambda_fn_script_name = "lambda_raw_download_categories"
  memory_size = 128
  timeout = 10
  tfm_role = module.iam.TFMRole_arn
  etl_lambda_layer_arn = aws_lambda_layer_version.etl_layer.arn
}

module "raw_product_categories" {
  # depends_on = [ module.raw_categories ]
  source = "./lambdas"
  lambda_fn_name = "raw_download_product_category"
  lambda_fn_script_name = "lambda_raw_download_product_category"
  memory_size = 512
  timeout = 60*5
  tfm_role = module.iam.TFMRole_arn
  etl_lambda_layer_arn = aws_lambda_layer_version.etl_layer.arn
}

module "bronze_categories" {
  # depends_on = [ module.raw_product_categories ]
  source = "./lambdas"
  lambda_fn_name = "bronze_categories"
  lambda_fn_script_name = "lambda_bronze_categories"
  memory_size = 256
  timeout = 60
  tfm_role = module.iam.TFMRole_arn
  etl_lambda_layer_arn = aws_lambda_layer_version.etl_layer.arn
}

module "silver_products" {
  # depends_on = [ module.bronze_categories ]
  source = "./lambdas"
  lambda_fn_name = "silver_products"
  lambda_fn_script_name = "lambda_silver_products"
  memory_size = 1024
  timeout = 60*4
  tfm_role = module.iam.TFMRole_arn
  etl_lambda_layer_arn = aws_lambda_layer_version.etl_layer.arn
}

module "gold_categories" {
  # depends_on = [ module.silver_products ]
  source = "./lambdas"
  lambda_fn_name = "gold_categories"
  lambda_fn_script_name = "lambda_gold_categories"
  memory_size = 1024
  timeout = 60*5
  tfm_role = module.iam.TFMRole_arn
  etl_lambda_layer_arn = aws_lambda_layer_version.etl_layer.arn
}

module "gold_products" {
  # depends_on = [ module.gold_categories ]
  source = "./lambdas"
  lambda_fn_name = "gold_products"
  lambda_fn_script_name = "lambda_gold_products"
  memory_size = 1024
  timeout = 60*5
  tfm_role = module.iam.TFMRole_arn
  etl_lambda_layer_arn = aws_lambda_layer_version.etl_layer.arn
}

module "gold_locations" {
  # depends_on = [ module.gold_products ]
  source = "./lambdas"
  lambda_fn_name = "gold_locations"
  lambda_fn_script_name = "lambda_gold_locations"
  memory_size = 1024
  timeout = 60*5
  tfm_role = module.iam.TFMRole_arn
  etl_lambda_layer_arn = aws_lambda_layer_version.etl_layer.arn
}
