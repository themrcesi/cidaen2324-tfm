########################## ECR & ECR ###############################

resource "aws_ecr_repository" "bronze_products" {
  name                 = var.ecr_bronze_products_repository_name
  image_tag_mutability = "MUTABLE"   # Optional: Set to IMMUTABLE if you want image tags to be immutable
  image_scanning_configuration {
    scan_on_push = true   # Optional: Enable image scanning on push
  }
  encryption_configuration {
    encryption_type = "AES256"   # Optional: Specify encryption type, default is AES256
  }
}

resource "aws_ecs_cluster" "fargate_cluster" {
  name = var.ecs_pipeline_cluster_name
}

resource "null_resource" "build_push_dkr_img" {
  # triggers = {
  #   detect_docker_source_changes = var.force_image_rebuild == true ? timestamp() : local.dkr_img_src_sha256
  # }
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
      name      = "bronze_products"
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

############################## LAMBDAS ###################################
module "raw_categories" {
  source = "./lambdas"
  lambda_fn_name = "raw_download_categories_dev"
  lambda_fn_script_name = "lambda_raw_download_categories"
  memory_size = 128
  timeout = 10
  tfm_role = local.tfm_role
}

module "raw_product_categories" {
  # depends_on = [ module.raw_categories ]
  source = "./lambdas"
  lambda_fn_name = "raw_download_product_category_dev"
  lambda_fn_script_name = "lambda_raw_download_product_category"
  memory_size = 512
  timeout = 60*5
  tfm_role = local.tfm_role
}

module "bronze_categories" {
  # depends_on = [ module.raw_product_categories ]
  source = "./lambdas"
  lambda_fn_name = "bronze_categories_dev"
  lambda_fn_script_name = "lambda_bronze_categories"
  memory_size = 256
  timeout = 60
  tfm_role = local.tfm_role
}

module "silver_products" {
  # depends_on = [ module.bronze_categories ]
  source = "./lambdas"
  lambda_fn_name = "silver_products_dev"
  lambda_fn_script_name = "lambda_silver_products"
  memory_size = 1024
  timeout = 60*4
  tfm_role = local.tfm_role
}

module "gold_categories" {
  # depends_on = [ module.silver_products ]
  source = "./lambdas"
  lambda_fn_name = "gold_categories_dev"
  lambda_fn_script_name = "lambda_gold_categories"
  memory_size = 1024
  timeout = 60*5
  tfm_role = local.tfm_role
}

module "gold_products" {
  # depends_on = [ module.gold_categories ]
  source = "./lambdas"
  lambda_fn_name = "gold_products_dev"
  lambda_fn_script_name = "lambda_gold_products"
  memory_size = 1024
  timeout = 60*5
  tfm_role = local.tfm_role
}

module "gold_locations" {
  # depends_on = [ module.gold_products ]
  source = "./lambdas"
  lambda_fn_name = "gold_locations_dev"
  lambda_fn_script_name = "lambda_gold_locations"
  memory_size = 1024
  timeout = 60*5
  tfm_role = local.tfm_role
}
