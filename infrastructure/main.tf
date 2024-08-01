########################### ECR & ECR ###############################

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
  task_role_arn            = var.tfm_role
  execution_role_arn       = var.tfm_role

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
resource "null_resource" "create_lambda_zip_bronze_categories" {
  provisioner "local-exec" {
    command = <<EOT
      cd ../src/infra
      echo $PWD
      zip -r9 ../../lambda_function.zip lambda_bronze_categories.py
    EOT
  }
  # Add a trigger to force the creation of the ZIP file if the source file changes
  triggers = {
    always_run = "${timestamp()}"
  }
}

resource "aws_lambda_function" "bronze_categories" {
  depends_on = [null_resource.create_lambda_zip_bronze_categories]

  function_name = "bronze_categories_dev"
  role          = var.tfm_role
  handler       = "lambda_bronze_categories.lambda_handler"
  runtime       = "python3.10"
  memory_size   = 512
  timeout       = 60
  architectures = ["arm64"]

  layers = [var.etl_lambda_layer]

  environment {
    variables = {
      LOG_LEVEL = "DEBUG"
    }
  }

  filename         = "${path.module}/../lambda_function.zip"
  # source_code_hash = filebase64sha256("${path.module}/../lambda_function.zip")
}

resource "null_resource" "cleanup_lambda_zip_bronze_categories" {
  provisioner "local-exec" {
    command = "rm -f ${path.module}/../lambda_function.zip"
  }
  triggers = {
    always_run = "${timestamp()}"
  }
}

resource "null_resource" "create_lambda_zip_bronze_products" {
  provisioner "local-exec" {
    command = <<EOT
      cd ../src/infra
      echo $PWD
      zip -r9 ../../lambda_function.zip lambda_bronze_products.py
    EOT
  }
  # Add a trigger to force the creation of the ZIP file if the source file changes
  triggers = {
    always_run = "${timestamp()}"
  }
}

resource "aws_lambda_function" "bronze_products" {
  depends_on = [null_resource.create_lambda_zip_bronze_products]

  function_name = "bronze_products_dev"
  role          = var.tfm_role
  handler       = "lambda_bronze_products.lambda_handler"
  runtime       = "python3.10"
  memory_size   = 512
  timeout       = 60
  architectures = ["arm64"]

  layers = [var.etl_lambda_layer]

  environment {
    variables = {
      LOG_LEVEL = "DEBUG"
    }
  }

  filename         = "${path.module}/../lambda_function.zip"
  # source_code_hash = filebase64sha256("${path.module}/../lambda_function.zip")
}

resource "null_resource" "cleanup_lambda_zip_bronze_products" {
  provisioner "local-exec" {
    command = "rm -f ${path.module}/../lambda_function.zip"
  }
  triggers = {
    always_run = "${timestamp()}"
  }
}

